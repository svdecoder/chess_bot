import os
import sys
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import attacks
from constants import *
from position import Position
from moveGenerator import generateMoves, applyMove, isInCheck, colorOf, opponentOf


PIECE_LETTERS = {QUEEN: "q", ROOK: "r", BISHOP: "b", KNIGHT: "n"}
LETTER_TO_PIECE = {v: k for k, v in PIECE_LETTERS.items()}


def parseSquare(text):
    file = ord(text[0]) - ord('a')
    rank = int(text[1]) - 1
    return rank * 8 + file


def squareName(square):
    file = "abcdefgh"[square % 8]
    rank = square // 8 + 1
    return f"{file}{rank}"


def parseUserMove(text, legalMoves):
    text = text.strip().lower()
    if len(text) not in (4, 5):
        return None

    try:
        start = parseSquare(text[0:2])
        end = parseSquare(text[2:4])
    except (IndexError, ValueError):
        return None

    promoting = LETTER_TO_PIECE.get(text[4]) if len(text) == 5 else None

    for move in legalMoves:
        if move.start == start and move.end == end:
            if move.isPromoting():
                if promoting == move.promotionPiece():
                    return move
            elif promoting is None:
                return move
    return None


def gameResult(position, legalMoves):
    color = colorOf(position)
    if legalMoves:
        if position.halfmoveClock >= 100:
            return "Draw by the fifty-move rule."
        return None
    if isInCheck(position, color):
        winner = "Black" if color == WHITE else "White"
        return f"Checkmate. {winner} wins."
    return "Stalemate. Draw."


def printMoves(legalMoves):
    print("Legal moves:", " ".join(str(m) for m in legalMoves))


def main():
    attacks.init()
    position = Position()

    print("Simple CLI chess. Enter moves like 'e2e4' or 'e7e8q' for promotion.")
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

        userInput = input(f"{sideName} to move: ").strip()

        if userInput.lower() == "quit":
            break
        if userInput.lower() == "moves":
            printMoves(legalMoves)
            continue

        move = parseUserMove(userInput, legalMoves)
        if move is None:
            print("Illegal or unrecognized move. Type 'moves' to see legal moves.")
            continue

        applyMove(position, move)


if __name__ == "__main__":
    main()