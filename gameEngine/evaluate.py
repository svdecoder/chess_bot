import sys
import os
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from constants import TOTAL_PHASE, PHASE_WEIGHTS, PIECE_VALUES, WHITE, BLACK
from pst import PST_MIDDLEGAME, PST_ENDGAME

def getGamePhase(position):
    phaseSum = 0
    for square in range(64):
        data = position.getPiece(square)
        if data != None:
            color, piece = data
            phaseSum += PHASE_WEIGHTS[piece]
    phaseSum = min(phaseSum, TOTAL_PHASE)
    gamePhase = phaseSum / TOTAL_PHASE
    return gamePhase

def materialScore(position):
    score = 0
    for square in range(64):
        data = position.getPiece(square)
        if data != None:
            color, piece = data
            if color == WHITE:
                score += PIECE_VALUES[piece]
            else:
                score -= PIECE_VALUES[piece]
    return score

def positionalScore(position, gamePhase):
    score = 0
    for square in range(64):
        data = position.getPiece(square)
        if data != None:
            color, piece = data
            if color == WHITE:
                pstSquare = square
            else:
                pstSquare = square ^ 56
            middleGameValue = PST_MIDDLEGAME[piece][pstSquare]
            endGameValue = PST_ENDGAME[piece][pstSquare]
            interpolated = middleGameValue * gamePhase + endGameValue * (1 - gamePhase)
            if color == WHITE:
                score += interpolated
            else:
                score -= interpolated
    return score

def evaluate(position):
    gamePhase = getGamePhase(position)
    total = materialScore(position) + positionalScore(position, gamePhase)
    if position.sideToMove == 0:
        return total
    else:
        return -total
    # Note: position.sideToMove uses its own 0/1 encoding (see position.py),
    # separate from the WHITE/BLACK piece-color constants (0/6) -- 0 happens
    # to line up with WHITE either way, but don't compare it against BLACK.