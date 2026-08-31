import os
import sys
import argparse
import time

sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gameCore'))
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gameEngine'))

import numpy as np

from position import Position
from moveGenerator import generateLegalMoves, colorOf, applyMove, isInCheck
from constants import WHITE
from engine import Engine
from network import ValueNetwork, makeEvalFn, SCORE_SCALE
from features import positionToFeatures


def gameOutcomeWhitePOV(position, legalMoves, plyCount, maxPlies):
    color = colorOf(position)
    if not legalMoves:
        if isInCheck(position, color):
            return -1.0 if color == WHITE else 1.0
        return 0.0
    if position.halfmoveClock >= 100 or plyCount >= maxPlies:
        return 0.0
    return None


def playSelfPlayGame(engine, maxPlies=150):
    position = Position()
    featuresList = []
    ply = 0

    while True:
        legalMoves = generateLegalMoves(position, colorOf(position))
        outcome = gameOutcomeWhitePOV(position, legalMoves, ply, maxPlies)
        if outcome is not None:
            return featuresList, outcome

        featuresList.append(positionToFeatures(position))

        move = engine.findBestMove(position)
        if move is None:
            return featuresList, 0.0

        newPosition = position.copy()
        applyMove(newPosition, move)
        position = newPosition
        ply += 1


def generateGames(numGames, outPath, timeLimit=0.5, maxDepth=4, maxPlies=150,
                   networkPath=None, verboseEngine=False):
    evalFn = None
    if networkPath is not None:
        evalFn = makeEvalFn(ValueNetwork.load(networkPath))

    engine = Engine(evalFn=evalFn, timeLimit=timeLimit, maxDepth=maxDepth, verbose=verboseEngine)

    allFeatures = []
    allTargets = []

    startTime = time.time()
    for gameIndex in range(numGames):
        featuresList, outcome = playSelfPlayGame(engine, maxPlies=maxPlies)
        allFeatures.extend(featuresList)
        allTargets.extend([outcome * SCORE_SCALE] * len(featuresList))

        print(f"game {gameIndex + 1}/{numGames}  positions {len(featuresList)}  "
              f"outcome(white) {outcome:+.0f}  total positions so far {len(allFeatures)}  "
              f"elapsed {time.time() - startTime:.1f}s")

    X = np.stack(allFeatures).astype(np.float32)
    y = np.array(allTargets, dtype=np.float32)
    np.savez(outPath, X=X, y=y)
    print(f"Saved {len(allTargets)} positions from {numGames} games to {outPath}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate self-play training data.")
    parser.add_argument("--games", type=int, default=20)
    parser.add_argument("--out", type=str, default="training/data/selfplay.npz")
    parser.add_argument("--time-limit", type=float, default=0.5)
    parser.add_argument("--max-depth", type=int, default=4)
    parser.add_argument("--max-plies", type=int, default=150)
    parser.add_argument("--network", type=str, default=None)
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    generateGames(
        numGames=args.games,
        outPath=args.out,
        timeLimit=args.time_limit,
        maxDepth=args.max_depth,
        maxPlies=args.max_plies,
        networkPath=args.network,
    )
