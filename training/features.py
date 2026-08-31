import os
import sys

sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gameCore'))

import numpy as np

NUM_FEATURES = 12 * 64 + 1 + 4


def positionToFeatures(position):
    features = np.zeros(NUM_FEATURES, dtype=np.float32)

    for square in range(64):
        data = position.getPiece(square)
        if data is not None:
            color, piece = data
            features[(color + piece) * 64 + square] = 1.0

    offset = 12 * 64
    features[offset] = 1.0 if position.sideToMove == 0 else 0.0
    for i in range(4):
        features[offset + 1 + i] = 1.0 if position.castlingRights[i] else 0.0

    return features
