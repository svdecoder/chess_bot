# chess_bot

A from-scratch bitboard chess engine in Python: legal move generation, alpha-beta
search with a transposition table, a classical hand-written evaluator, and an
optional trained value network that can replace that evaluator at search time.

## Layout

```
constants.py        shared constants for every module below (piece/color ids,
                     move tags, search bounds, TT flags, PST/eval weights)

gameCore/            rules engine -- knows nothing about search or evaluation
  bitboard.py          Bitboard: a 64-bit mask with set/clear/toggle/pop helpers
  attacks.py            precomputed attack tables (pawns, knights, kings) and
                       magic-free sliding attacks (bishop/rook/queen)
  move.py               Move: start/end/tag/promotion, plus __str__ as "e2e4"
  position.py           Position: 12 piece bitboards, side to move, castling
                       rights, en passant square, move/halfmove clocks
  moveGenerator.py      pseudo-legal + legal move generation, applyMove,
                       isInCheck, colorOf/opponentOf
  main.py                a minimal CLI to play a game against yourself, useful
                       for sanity-checking gameCore on its own
  data.py               GameState -- clock/history wrapper, not used by search

gameEngine/          search + evaluation, built entirely on gameCore
  zorbrist.py            Zobrist hashing: computeHash (from scratch) and
                       updateHashMove (incremental, since applyMove has no
                       matching unmakeMove)
  transposition.py       TTEntry + a plain dict-backed transposition table
                       (depth-preferred replacement, exact/lower/upper flags)
  evaluate.py             classical evaluator: material + tapered PST score,
                       returned from the side-to-move's perspective
  pst.py                  the piece-square tables evaluate.py reads, plus the
                       auto-update mechanism described below
  search.py               negamax + alpha-beta + quiescence search + the TT,
                       driven by iterative deepening
  engine.py               Engine: the one class other code should import --
                       wraps search() and lets the eval function be swapped

training/            self-play data generation + a small value network
  features.py             Position -> flat feature vector (773 floats)
  network.py               ValueNetwork: a torch MLP (773 -> 128 -> 32 -> 1),
                       trained with Adam on MSE against game outcomes
  selfplay.py               plays the engine against itself and records
                       (features, outcome) pairs to a .npz file
  train.py                   trains a ValueNetwork on one or more .npz files
  updatePst.py                derives learned piece-square tables from a
                       trained network -- see "Auto PST update" below
  autoTrain.py                 runs selfplay -> train -> updatePst in a loop
                       indefinitely -- see "Continuous training" below
  data/                      .npz self-play datasets land here (gitignored
                       except for .gitkeep)

playEngine.py        CLI: play a game against the engine (classical eval by
                     default, or a trained network with --network)
```

Every module resolves its imports by inserting the relevant sibling directory
onto `sys.path` at the top of the file, so any script can be run directly
(`python3 gameEngine/search.py`, `python3 training/train.py`, ...) without a
package install step.

## Playing a game

```
python3 playEngine.py --color white --time-limit 5
```

`--network training/weights.pt` swaps in a trained network as the evaluator
instead of the classical one; everything else about search (TT, move
ordering, quiescence) stays the same either way, since `engine.py` only cares
that `evalFn(position)` returns a centipawn-ish score for the side to move.

## Training loop

```
python3 training/selfplay.py --games 50 --out training/data/batch1.npz
python3 training/train.py --data "training/data/*.npz" --out training/weights.pt --update-pst
python3 playEngine.py --network training/weights.pt
```

`selfplay.py` also accepts `--network`, so once you have a trained network you
can generate the next batch of games with it instead of the classical
evaluator and retrain -- the usual self-play bootstrap loop.

### Running training on a GPU

`network.py` is built on `torch`. `ValueNetwork` picks `cuda` automatically at
import time if a GPU is visible (`torch.cuda.is_available()`), otherwise it
falls back to `cpu` -- nothing to configure in `train.py` or `selfplay.py`.

```
pip install torch --break-system-packages   # CUDA build if your machine has a GPU
python3 training/train.py --data "training/data/*.npz" --out training/weights.pt
```

To confirm which device a run is using:

```
python3 -c "from training.network import DEVICE; print(DEVICE)"
```

Two things matter most for actually getting a speedup:

- **Batch size.** The self-play defaults (`--time-limit`/`--max-depth`) keep
  games small, so a `training/data/*.npz` glob might only be a few thousand
  positions. A GPU mostly pays off once `--batch-size` is large enough (a few
  thousand) that each `trainStep` call is doing real matrix-multiply work
  instead of being dominated by Python/kernel-launch overhead -- try bumping
  `--batch-size` well above the default 256 once you have enough data.
- **Where the bottleneck actually is.** `selfplay.py` is bottlenecked by the
  Python move generator and search in `gameCore`/`gameEngine`, not by network
  inference -- moving `ValueNetwork` to a GPU speeds up `train.py`, not game
  generation. If self-play itself is the slow part, generate more games (more
  `--games`, more parallel processes) rather than expecting a GPU to help there.

`network.save`/`ValueNetwork.load` now write/read torch checkpoints (`.pt`),
not `.npz` -- unrelated to the self-play data files in `training/data/`, which
stay plain numpy arrays (`X`, `y`) either way.

## Auto PST update

The value network and the classical evaluator's piece-square tables are two
separate ways of scoring a position, and normally improvements to one don't
carry over to the other -- you'd have to look at what the network learned and
hand-copy new numbers into `pst.py`. `training/updatePst.py` automates that
step:

1. It builds a baseline feature vector: two lone kings, nobody else on the
   board, white to move.
2. For every non-king piece and every square, it adds that one piece to the
   baseline and asks the trained network for a score. Subtracting the
   baseline score and the piece's material value (`PIECE_VALUES` in
   `constants.py`) leaves the network's purely positional opinion of that
   piece on that square -- the same quantity a piece-square table entry
   represents.
3. Those 64 values per piece are written to `gameEngine/data/learned_pst.json`.
4. `gameEngine/pst.py` checks for that file on import and overlays any tables
   it finds on top of the hardcoded defaults, silently keeping the defaults
   for anything the file doesn't cover.

Run it standalone:

```
python3 training/updatePst.py --network training/weights.pt
```

or automatically at the end of a training run:

```
python3 training/train.py --data "training/data/*.npz" --out training/weights.pt --update-pst
```

Either way, the next time anything imports `gameEngine.evaluate` -- including
`playEngine.py` with no `--network` flag at all -- it picks up the
network-derived tables instead of the original hand-picked ones. No manual
copy-pasting, and the classical evaluator keeps compounding gains from every
training run instead of only the network eval path benefiting.

**Known simplification:** the network has no explicit game-phase input, so a
single probe can't separate a middlegame table from an endgame one the way
the hardcoded `PAWN_MG`/`PAWN_EG` pair does. `updatePst.py` currently writes
the same learned table for both phases. Probing with reduced material on the
board (to approximate an endgame) or adding a phase feature to `features.py`
would be the natural next step if that turns out to matter in practice.

## Continuous training

`training/autoTrain.py` runs the selfplay -> train -> updatePst cycle
indefinitely instead of one-off manual commands:

```
python3 training/autoTrain.py
```

Each cycle it: generates `--games-per-cycle` self-play games to a new,
uniquely-named file under `--data-dir`; trains on every `.npz` file in that
directory (resuming from `--weights` if it already exists); and refreshes
`gameEngine/data/learned_pst.json` from the freshly-trained network (disable
with `--no-update-pst`). Progress prints as it happens -- game-by-game from
self-play, epoch-by-epoch from training, then a per-cycle summary line with
the device in use, cycle duration, and total elapsed time.

**Stopping it:** type `stop` and press Enter at any point. This doesn't
interrupt anything mid-flight -- the script finishes the self-play batch and
training pass already in progress, saves the weights, updates the PST file,
prints a final summary, and only then exits. Ctrl+C does the same thing (it's
caught and treated as a stop request, not a hard kill), which matters if your
terminal isn't feeding the script's stdin (e.g. it's running under a process
manager).

By default self-play always uses the classical evaluator, the same as
running `selfplay.py` directly. Pass `--bootstrap` to switch to the
self-play-with-the-network-you're-training loop once weights exist from a
prior cycle:

```
python3 training/autoTrain.py --bootstrap --games-per-cycle 50 --epochs-per-cycle 10
```

Since `--data-dir` accumulates every cycle's file and each cycle retrains on
the whole directory, both the per-cycle training cost and disk usage grow the
longer the script runs -- fine for a while, but worth periodically archiving
old `training/data/*.npz` files out of the directory (or lowering
`--epochs-per-cycle`) for very long-running sessions.



`search.py` clears the transposition table automatically whenever the active
`evalFn` changes between calls (classical -> network or vice versa), since a
cached score is only meaningful for the evaluator that produced it. This is
handled inside `search()` / `engine.py` -- callers don't need to think about
it, including when switching evaluators mid-session via `playEngine.py
--network`.
