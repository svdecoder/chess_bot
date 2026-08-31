import os
import sys
import json
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from constants import PAWN, KNIGHT, BISHOP, ROOK, KING, QUEEN

PAWN_MG = [
      0,   0,   0,   0,   0,   0,   0,   0,
      5,  10,  10, -20, -20,  10,  10,   5,
      5,  -5, -10,   0,   0, -10,  -5,   5,
      0,   0,   0,  20,  20,   0,   0,   0,
      5,   5,  10,  25,  25,  10,   5,   5,
     10,  10,  20,  30,  30,  20,  10,  10,
     50,  50,  50,  50,  50,  50,  50,  50,
      0,   0,   0,   0,   0,   0,   0,   0,
]

KNIGHT_MG = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20,   0,   5,   5,   0, -20, -40,
    -30,   5,  10,  15,  15,  10,   5, -30,
    -30,   0,  15,  20,  20,  15,   0, -30,
    -30,   5,  15,  20,  20,  15,   5, -30,
    -30,   0,  10,  15,  15,  10,   0, -30,
    -40, -20,   0,   0,   0,   0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50,
]

BISHOP_MG = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10,   5,   0,   0,   0,   0,   5, -10,
    -10,  10,  10,  10,  10,  10,  10, -10,
    -10,   0,  10,  10,  10,  10,   0, -10,
    -10,   5,   5,  10,  10,   5,   5, -10,
    -10,   0,   5,  10,  10,   5,   0, -10,
    -10,   0,   0,   0,   0,   0,   0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20,
]

ROOK_MG = [
      0,   0,   0,   5,   5,   0,   0,   0,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
      5,  10,  10,  10,  10,  10,  10,   5,
      0,   0,   0,   0,   0,   0,   0,   0,
]

QUEEN_MG = [
    -20, -10, -10,  -5,  -5, -10, -10, -20,
    -10,   0,   5,   0,   0,   0,   0, -10,
    -10,   5,   5,   5,   5,   5,   0, -10,
      0,   0,   5,   5,   5,   5,   0,  -5,
     -5,   0,   5,   5,   5,   5,   0,  -5,
    -10,   0,   5,   5,   5,   5,   0, -10,
    -10,   0,   0,   0,   0,   0,   0, -10,
    -20, -10, -10,  -5,  -5, -10, -10, -20,
]

KING_MG = [
     20,  30,  10,   0,   0,  10,  30,  20,
     20,  20,   0,   0,   0,   0,  20,  20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
]

KING_EG = [
    -50, -30, -30, -30, -30, -30, -30, -50,
    -30, -30,   0,   0,   0,   0, -30, -30,
    -30, -10,  20,  30,  30,  20, -10, -30,
    -30, -10,  30,  40,  40,  30, -10, -30,
    -30, -10,  30,  40,  40,  30, -10, -30,
    -30, -10,  20,  30,  30,  20, -10, -30,
    -30, -20, -10,   0,   0, -10, -20, -30,
    -50, -40, -30, -20, -20, -30, -40, -50,
]

# Simplified starting point: only pawns and king get distinct endgame
# tables (pawns favor pushing, king favors centralizing). Knights,
# bishops, rooks, and queens reuse their middlegame tables for now --
# worth revisiting once the rest of the engine is working.
PAWN_EG = PAWN_MG
KNIGHT_EG = KNIGHT_MG
BISHOP_EG = BISHOP_MG
ROOK_EG = ROOK_MG
QUEEN_EG = QUEEN_MG

PST_MIDDLEGAME = {
    PAWN: PAWN_MG,
    KNIGHT: KNIGHT_MG,
    BISHOP: BISHOP_MG,
    ROOK: ROOK_MG,
    QUEEN: QUEEN_MG,
    KING: KING_MG,
}

PST_ENDGAME = {
    PAWN: PAWN_EG,
    KNIGHT: KNIGHT_EG,
    BISHOP: BISHOP_EG,
    ROOK: ROOK_EG,
    QUEEN: QUEEN_EG,
    KING: KING_EG,
}

LEARNED_PST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'learned_pst.json')
PIECE_NAME_TO_ID = {"PAWN": PAWN, "KNIGHT": KNIGHT, "BISHOP": BISHOP, "ROOK": ROOK, "QUEEN": QUEEN, "KING": KING}


def loadLearnedPST(path=LEARNED_PST_PATH):
    if not os.path.isfile(path):
        return False

    try:
        with open(path) as f:
            learned = json.load(f)
    except (OSError, ValueError):
        return False

    loadedAnything = False
    for phase, tables in (("middlegame", PST_MIDDLEGAME), ("endgame", PST_ENDGAME)):
        phaseData = learned.get(phase, {})
        for pieceName, pieceId in PIECE_NAME_TO_ID.items():
            values = phaseData.get(pieceName)
            if isinstance(values, list) and len(values) == 64:
                tables[pieceId] = values
                loadedAnything = True

    return loadedAnything


loadLearnedPST()
