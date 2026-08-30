from bitboard import Bitboard as BT
from constants import *

class Position:
    def __init__(self):
        self.position = [
        BT(0b0000000000000000000000000000000000000000000000001111111100000000),
        BT(0b0000000000000000000000000000000000000000000000000000000001000010),
        BT(0b0000000000000000000000000000000000000000000000000000000000100100),
        BT(0b0000000000000000000000000000000000000000000000000000000010000001),
        BT(0b0000000000000000000000000000000000000000000000000000000000010000),
        BT(0b0000000000000000000000000000000000000000000000000000000000001000),
        BT(0b0000000011111111000000000000000000000000000000000000000000000000),
        BT(0b0100001000000000000000000000000000000000000000000000000000000000),
        BT(0b0010010000000000000000000000000000000000000000000000000000000000),
        BT(0b1000000100000000000000000000000000000000000000000000000000000000),
        BT(0b0001000000000000000000000000000000000000000000000000000000000000),
        BT(0b0000100000000000000000000000000000000000000000000000000000000000)
        ]
        #0 = white, 1 = black
        self.sideToMove = 0
        #0 = white kingside, 1 = white queenside, 2 = black kingside, 3 = black queenside
        self.castlingRights = [True, True, True, True]
        self.enPassant = -1
        self.halfmoveClock = 0
        self.fullmoveClock = 0

    def clear(self):
        for i in range (12):
            self.position[i] = BT(0b0000000000000000000000000000000000000000000000000000000000000000)
        self.sideToMove = 0
        self.castlingRights = [True, True, True, True]
        self.enPassant = -1
        self.halfmoveClock = 0
        self.fullmoveClock = 0
    
    def copy(self):
        copyPosition = Position()
        copyPosition.position = [
            BT(bb.bitboard) for bb in self.position
        ]
        copyPosition.sideToMove = self.sideToMove
        copyPosition.castlingRights = self.castlingRights.copy()
        copyPosition.enPassant = self.enPassant
        copyPosition.halfmoveClock = self.halfmoveClock
        copyPosition.fullmoveClock = self.fullmoveClock
        return copyPosition

    def reset(self):
        self.__init__()
        
    def checkPosition(self, square):
        for bitboardToCheck in range (12):
            if self.position[bitboardToCheck].checkValue(square):
                return (True, bitboardToCheck)
        return (False, -1)
    
    def isEmpty(self, square):
        answer, bitboard = self.checkPosition(square)
        return not answer
    
    def occupancy(self, color):
        positions = BT(0b0000000000000000000000000000000000000000000000000000000000000000)
        if color == WHITE or color == BOTH:
            for i in range (6):
                positions |= self.position[i]
        if color == BLACK or color == BOTH:
            for i in range (6):
                positions |= self.position[i + 6]
        elif color == EMPTY:
            positions = BT(0b1111111111111111111111111111111111111111111111111111111111111111)
            for i in range(12):
                positions &= ~self.position[i]
        return positions
    
    def getPiece(self, square):
        occupancy, piece = self.checkPosition(square)
        if not occupancy:
            return None
        else:
            if (piece < 6):
                return (WHITE, piece % 6)
            else:
                return (BLACK, piece % 6)
    
    def getPieceType(self, square):
        data = self.getPiece(square)
        if data != None:
            color, piece = data
            return piece
        else:
            return None
    
    def getColor(self, square):
        data = self.getPiece(square)
        if data != None:
            color, piece = data
            return color
        else:
            return None
    
    def isWhite(self, square):
        data = self.getColor(square)
        return data == WHITE

    def isBlack(self, square):
        data = self.getColor(square)
        return data == BLACK

    def contains(self, square, color, piece):
        return self.position[color + piece].checkValue(square)
    
    def getBitboard(self, color, piece):
        return self.position[color + piece]
    
    def placePiece(self, color, piece, square):
        if self.isEmpty(square):
            self.position[color + piece].setValue(square)
            return True
        else:
            return False
    
    def removePiece(self, square):
        result, pos = self.checkPosition(square)
        if not result:
            return None
        else:
            color, piece = self.getPiece(square)
            self.position[color + piece].clearValue(square)
            return (color, piece)
    
    def movePiece(self, start, end):
        if not self.isEmpty(end):
            self.removePiece(end)
        data = self.getPiece(start)
        if data:
            self.removePiece(start)
            color, piece = data
            self.placePiece(color, piece, end)
            
    def replacePiece(self, square, color, piece):
        self.removePiece(square)
        self.placePiece(color, piece, square)
    
    def kingSquare(self, color):
        return self.position[color + KING].positionLSB()

    def pieceCount(self, color):
        numberOfPiece = 0
        if color == BOTH:
            for i in range(12):
                numberOfPiece += self.position[i].countValue()
        elif color == EMPTY:
            numberOfPiece = 64 - self.pieceCount(BOTH)
        else:
            for i in range(6):
                numberOfPiece += self.position[color + i].countValue()
        return numberOfPiece
    
    def __str__(self):
        pieceSymbols = {
            (WHITE, PAWN): "P",
            (WHITE, KNIGHT): "N",
            (WHITE, BISHOP): "B",
            (WHITE, ROOK): "R",
            (WHITE, KING): "K",
            (WHITE, QUEEN): "Q",

            (BLACK, PAWN): "p",
            (BLACK, KNIGHT): "n",
            (BLACK, BISHOP): "b",
            (BLACK, ROOK): "r",
            (BLACK, KING): "k",
            (BLACK, QUEEN): "q",
        }

        output = ""

        for rank in range(7, -1, -1):
            output += str(rank + 1) + " "

            for file in range(8):
                square = rank * 8 + file

                piece = self.getPiece(square)

                if piece is None:
                    output += ". "
                else:
                    output += pieceSymbols[piece] + " "

            output += "\n"

        output += "  a b c d e f g h"

        return output