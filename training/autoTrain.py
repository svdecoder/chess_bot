import os
import sys
import time
import glob
import argparse
import threading
from datetime import datetime

sys.path.insert(1, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gameCore'))
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gameEngine'))

from selfplay import generateGames
from train import train
from updatePst import updateLearnedPST
from network import DEVICE

stopRequested = threading.Event()


def listenForStop():
    while not stopRequested.is_set():
        try:
            line = input()
        except EOFError:
            return
        if line.strip().lower() == "stop":
            print("\n[autoTrain] 'stop' received -- finishing the current batch and training pass, then exiting.")
            stopRequested.set()
            return


def formatDuration(seconds):
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def runCycle(cycleIndex, args, runStart):
    cycleStart = time.time()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    batchPath = os.path.join(args.data_dir, f"autoplay_{cycleIndex:05d}_{timestamp}.npz")

    print(f"\n===== cycle {cycleIndex}  device={DEVICE}  elapsed={formatDuration(time.time() - runStart)} =====")

    selfplayNetwork = args.weights if (args.bootstrap and os.path.isfile(args.weights)) else None
    print(f"[autoTrain] generating {args.games_per_cycle} self-play games "
          f"({'network' if selfplayNetwork else 'classical'} eval) -> {batchPath}")
    generateGames(
        numGames=args.games_per_cycle,
        outPath=batchPath,
        timeLimit=args.time_limit,
        maxDepth=args.max_depth,
        maxPlies=args.max_plies,
        networkPath=selfplayNetwork,
    )

    resumeFrom = args.weights if os.path.isfile(args.weights) else None
    print(f"[autoTrain] training {'(resuming from ' + resumeFrom + ')' if resumeFrom else '(fresh network)'}")
    train(
        dataPattern=os.path.join(args.data_dir, "*.npz"),
        outPath=args.weights,
        epochs=args.epochs_per_cycle,
        batchSize=args.batch_size,
        learningRate=args.lr,
        resumeFrom=resumeFrom,
        updatePST=args.update_pst,
    )

    print(f"[autoTrain] cycle {cycleIndex} done in {formatDuration(time.time() - cycleStart)}  "
          f"total data files: {len(glob.glob(os.path.join(args.data_dir, '*.npz')))}")


def main(args):
    os.makedirs(args.data_dir, exist_ok=True)
    os.makedirs(os.path.dirname(args.weights) or ".", exist_ok=True)

    print(f"[autoTrain] starting on device={DEVICE}. Type 'stop' + Enter at any time to stop "
          f"after the current batch and training pass finish.")

    listener = threading.Thread(target=listenForStop, daemon=True)
    listener.start()

    runStart = time.time()
    cycleIndex = 0

    try:
        while not stopRequested.is_set():
            cycleIndex += 1
            runCycle(cycleIndex, args, runStart)
    except KeyboardInterrupt:
        print("\n[autoTrain] interrupted -- stopping after this cycle.")

    print(f"[autoTrain] stopped after {cycleIndex} cycle(s), "
          f"total time {formatDuration(time.time() - runStart)}. Weights saved at {args.weights}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run self-play + training indefinitely until stopped.")
    parser.add_argument("--data-dir", type=str, default="training/data")
    parser.add_argument("--weights", type=str, default="training/weights.pt")
    parser.add_argument("--games-per-cycle", type=int, default=20)
    parser.add_argument("--time-limit", type=float, default=0.5)
    parser.add_argument("--max-depth", type=int, default=4)
    parser.add_argument("--max-plies", type=int, default=150)
    parser.add_argument("--epochs-per-cycle", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--bootstrap", action="store_true",
                         help="once weights exist, self-play with the trained network instead of the classical evaluator")
    parser.add_argument("--no-update-pst", dest="update_pst", action="store_false",
                         help="skip refreshing gameEngine/data/learned_pst.json each cycle")
    args = parser.parse_args()

    main(args)
