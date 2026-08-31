import os
import sys
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from constants import *

class Move:
    def __init__(self, start, end, tag, promoting=None):
        if start < 0 or start > 63 or end < 0 or end > 63 or start == end:
            raise ValueError("Invalid piece case")
        if promoting is not None and promoting not in (QUEEN, ROOK, BISHOP, KNIGHT):
            raise ValueError("Invalid promotion piece")
        self.start = start
        self.end = end
        self.tag = tag
        self.promoting = promoting

    def copy(self):
        return Move(self.start, self.end, self.tag, self.promoting)
    
    def isCapture(self):
        return self.tag == CAPTURE or self.tag == PROMOTION_CAPTURE
    
    def isPromoting(self):
        if self.tag in (PROMOTION, PROMOTION_CAPTURE):
            if self.promoting is None:
                raise ValueError("Promotion move requires a promotion piece")
            return True
        else:
            if self.promoting is not None:
                raise ValueError("Only promotion moves may specify a promotion piece")
            return False

    def isKingsideCastle(self):
        return self.tag == KING_CASTLE
    
    def isQueensideCastle(self):
        return self.tag == QUEEN_CASTLE
    
    def isEnPassant(self):
        return self.tag == EN_PASSANT

    def isDoublePawnPush(self):
        return self.tag == DOUBLE_PAWN_PUSH
    
    def promotionPiece(self):
        return self.promoting
    
    def __eq__(self, move):
        if not isinstance(move, Move):
            return False
        return self.start == move.start and self.end == move.end and self.tag == move.tag and self.promoting == move.promoting
    
    def __str__(self):
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        startFile = alphabet[self.start % 8]
        startRank = self.start // 8 + 1
        endFile = alphabet[self.end % 8]
        endRank = self.end // 8 + 1
        promoLetters = {QUEEN: "q", ROOK: "r", BISHOP: "b", KNIGHT: "n"}
        suffix = promoLetters[self.promoting] if self.promoting is not None else ""
        return f"{startFile}{startRank}{endFile}{endRank}{suffix}"
    
    def __repr__(self):
        return str(self)