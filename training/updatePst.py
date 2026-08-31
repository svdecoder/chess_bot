import os
import sys
import json
import argparse

sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gameCore'))
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gameEngine'))

import numpy as np

from constants import PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING, WHITE, BLACK, PIECE_VALUES
from network import ValueNetwork
from features import NUM_FEATURES

PROBED_PIECES = (PAWN, KNIGHT, BISHOP, ROOK, QUEEN)
PIECE_ID_TO_NAME = {PAWN: "PAWN", KNIGHT: "KNIGHT", BISHOP: "BISHOP", ROOK: "ROOK", QUEEN: "QUEEN", KING: "KING"}
WHITE_KING_SQUARE = 4
BLACK_KING_SQUARE = 60


def baselineFeatures():
    features = np.zeros(NUM_FEATURES, dtype=np.float32)
    features[(WHITE + KING) * 64 + WHITE_KING_SQUARE] = 1.0
    features[(BLACK + KING) * 64 + BLACK_KING_SQUARE] = 1.0
    features[12 * 64] = 1.0
    return features


def probePieceOnSquare(network, baseline, piece, square):
    if square in (WHITE_KING_SQUARE, BLACK_KING_SQUARE):
        return None
    features = baseline.copy()
    features[(WHITE + piece) * 64 + square] = 1.0
    return float(network.predict(features.reshape(1, -1))[0])


def probePST(network):
    baseline = baselineFeatures()
    baselineScore = float(network.predict(baseline.reshape(1, -1))[0])

    tables = {}
    for piece in PROBED_PIECES:
        values = [0] * 64
        for square in range(64):
            score = probePieceOnSquare(network, baseline, piece, square)
            if score is not None:
                values[square] = round(score - baselineScore - PIECE_VALUES[piece])
        tables[piece] = values

    return tables


def updateLearnedPST(network, outPath=None):
    if outPath is None:
        outPath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '..', 'gameEngine', 'data', 'learned_pst.json'
        )

    tables = probePST(network)
    tablesByName = {PIECE_ID_TO_NAME[piece]: values for piece, values in tables.items()}
    learned = {"middlegame": tablesByName, "endgame": tablesByName}

    os.makedirs(os.path.dirname(outPath), exist_ok=True)
    with open(outPath, "w") as f:
        json.dump(learned, f, indent=2)

    print(f"Wrote learned PST for {len(tables)} piece types to {outPath}")
    return outPath


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Derive piece-square tables from a trained network.")
    parser.add_argument("--network", type=str, default="training/weights.pt")
    parser.add_argument("--out", type=str, default=None)
    args = parser.parse_args()

    net = ValueNetwork.load(args.network)
    updateLearnedPST(net, outPath=args.out)
