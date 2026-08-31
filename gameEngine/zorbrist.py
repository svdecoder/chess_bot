import sys
import os
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gameCore'))
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from constants import SEED
from position import *

import random

pieceKeys = []
castlingKeys = []
enPassantKeys = []
sideToMoveKey = 0

def initZobristKeys():
    global pieceKeys, castlingKeys, enPassantKeys, sideToMoveKey
    rng = random.Random(SEED)
    for pieces in range(12):
        pieceHashes = []
        for squares in range(64):
            computedHash = rng.getrandbits(64)
            pieceHashes.append(computedHash)
        pieceKeys.append(pieceHashes)
    for castling in range(4):
        computedHash = rng.getrandbits(64)
        castlingKeys.append(computedHash)
    for file in range(8):
        computedHash = rng.getrandbits(64)
        enPassantKeys.append(computedHash)
    sideToMoveKey = rng.getrandbits(64)

def computeHash(position):
    computedHash = 0
    for square in range(64):
        data = position.getPiece(square)
        if data != None:
            color, piece = data
            computedHash ^= pieceKeys[color + piece][square]
    for i in range(4):
        if position.castlingRights[i] == True:
            computedHash ^= castlingKeys[i]
    if position.enPassant != -1:
        file = position.enPassant % 8
        computedHash ^= enPassantKeys[file]
    if position.sideToMove != 0:
        computedHash ^= sideToMoveKey
    return computedHash

def updateHashMove(hash, move, oldPosition, newPosition):
    """
    Incrementally updates a Zobrist hash for a single move.

    Since this codebase has no unmakeMove (applyMove mutates in place, and
    legal-move checking relies on position.copy() + applyMove), this needs
    BOTH a pre-move snapshot (oldPosition) and the post-move result
    (newPosition) to work out what changed:
        newPosition = oldPosition.copy()
        applyMove(newPosition, move)
        hash = updateHashMove(hash, move, oldPosition, newPosition)
    """
    color, piece = oldPosition.getPiece(move.start)

    # Remove the moving piece from its origin square.
    hash ^= pieceKeys[color + piece][move.start]

    # Remove the old en passant key (if one was active before this move).
    if oldPosition.enPassant != -1:
        file = oldPosition.enPassant % 8
        hash ^= enPassantKeys[file]

    # Add the new en passant key (if this move created one).
    if newPosition.enPassant != -1:
        file = newPosition.enPassant % 8
        hash ^= enPassantKeys[file]

    # Ordinary or promotion capture: remove the captured piece from move.end.
    # Must read this from oldPosition -- on newPosition, move.end now holds
    # the mover (or the promoted piece), not the captured piece.
    if move.tag == CAPTURE or move.tag == PROMOTION_CAPTURE:
        capColor, capPiece = oldPosition.getPiece(move.end)
        hash ^= pieceKeys[capColor + capPiece][move.end]

    # En passant: captured pawn sits behind move.end, not on it.
    if move.tag == EN_PASSANT:
        if color == WHITE:
            hash ^= pieceKeys[BLACK + PAWN][move.end - 8]
        else:
            hash ^= pieceKeys[WHITE + PAWN][move.end + 8]

    # Place the piece on the destination square: the promoted piece for any
    # promotion (plain or capture), otherwise the original moving piece.
    if move.tag == PROMOTION or move.tag == PROMOTION_CAPTURE:
        hash ^= pieceKeys[color + move.promoting][move.end]
    else:
        hash ^= pieceKeys[color + piece][move.end]

    # Castling: also move the rook.
    if move.tag == KING_CASTLE:
        if color == WHITE:
            hash ^= pieceKeys[WHITE + ROOK][7]
            hash ^= pieceKeys[WHITE + ROOK][5]
        else:
            hash ^= pieceKeys[BLACK + ROOK][63]
            hash ^= pieceKeys[BLACK + ROOK][61]
    if move.tag == QUEEN_CASTLE:
        if color == WHITE:
            hash ^= pieceKeys[WHITE + ROOK][0]
            hash ^= pieceKeys[WHITE + ROOK][3]
        else:
            hash ^= pieceKeys[BLACK + ROOK][56]
            hash ^= pieceKeys[BLACK + ROOK][59]

    # Castling rights: only toggle the bits that actually changed.
    for i in range(4):
        if oldPosition.castlingRights[i] != newPosition.castlingRights[i]:
            hash ^= castlingKeys[i]

    # Side to move always flips.
    hash ^= sideToMoveKey

    return hash


initZobristKeys()

if __name__ == "__main__":
    assert len(pieceKeys) == 12 and all(len(p) == 64 for p in pieceKeys)
    assert len(castlingKeys) == 4
    assert len(enPassantKeys) == 8
    assert sideToMoveKey != 0
    print("Zobrist keys initialized OK")