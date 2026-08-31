import os
import sys
import argparse

sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gameCore'))
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gameEngine'))
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'training'))

import attacks
from constants import *
from position import Position
from moveGenerator import generateMoves, applyMove, isInCheck, colorOf
from main import parseUserMove, gameResult, printMoves
from engine import Engine


def loadEvalFn(networkPath):
    if networkPath is None:
        return None
    from network import ValueNetwork, makeEvalFn
    network = ValueNetwork.load(networkPath)
    return makeEvalFn(network)


def playAgainstEngine(humanColor, timeLimit, maxDepth, networkPath):
    attacks.init()
    position = Position()
    engine = Engine(evalFn=loadEvalFn(networkPath), timeLimit=timeLimit, maxDepth=maxDepth, verbose=True)

    print("Playing against chess_bot. Enter moves like 'e2e4' or 'e7e8q' for promotion.")
    print("Type 'moves' to list legal moves, 'quit' to exit.\n")

    while True:
        print()
        print(position)
        legalMoves = generateMoves(position)

        result = gameResult(position, legalMoves)
        if result:
            print(result)
            break

        color = colorOf(position)
        sideName = "White" if color == WHITE else "Black"
        if isInCheck(position, color):
            print(f"{sideName} is in check.")

        if color == humanColor:
            userInput = input(f"{sideName} (you) to move: ").strip()
            if userInput.lower() == "quit":
                break
            if userInput.lower() == "moves":
                printMoves(legalMoves)
                continue
            move = parseUserMove(userInput, legalMoves)
            if move is None:
                print("Illegal or unrecognized move. Type 'moves' to see legal moves.")
                continue
        else:
            print(f"{sideName} (engine) is thinking...")
            move = engine.findBestMove(position)
            print(f"Engine plays: {move}")

        applyMove(position, move)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Play a game against chess_bot.")
    parser.add_argument("--color", choices=["white", "black"], default="white", help="which side you play")
    parser.add_argument("--time-limit", type=float, default=5.0, help="seconds the engine thinks per move")
    parser.add_argument("--max-depth", type=int, default=64, help="max search depth (time limit usually hits first)")
    parser.add_argument("--network", type=str, default=None, help="path to a trained network (e.g. training/weights.pt) to use instead of the classical evaluator")
    args = parser.parse_args()

    humanColor = WHITE if args.color == "white" else BLACK
    playAgainstEngine(humanColor, args.time_limit, args.max_depth, args.network)
