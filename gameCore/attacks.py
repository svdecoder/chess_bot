import sys
import os
import sys
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from constants import *
from bitboard import Bitboard as BT

whitePawnAttacks = [BT() for _ in range(64)]
blackPawnAttacks = [BT() for _ in range(64)]
knightAttacks = [BT() for _ in range(64)]
kingAttacks = [BT() for _ in range(64)]
bishopMasks = [BT() for _ in range(64)]
rookMasks = [BT() for _ in range(64)]

def squareRank(square):
    return square // 8

def squareFile(square):
    return square % 8

def isOnBoard(rank, file):
    if 0 <= rank and 7 >= rank and 0 <= file and 7 >= file:
        return True
    else:
        return False

def makeSquare(rank, file):
    return rank * 8 + file

def generateWhitePawnAttacks(square):
    file = squareFile(square)
    rank = squareRank(square)
    board = BT()
    if isOnBoard(rank + 1, file + 1):
        board.setValue(square + 9)
    if isOnBoard(rank + 1, file - 1):
        board.setValue(square + 7)
    return board
        
def generateBlackPawnAttacks(square):
    file = squareFile(square)
    rank = squareRank(square)
    board = BT()
    if isOnBoard(rank - 1, file + 1):
        board.setValue(square - 7)
    if isOnBoard(rank - 1, file - 1):
        board.setValue(square - 9)
    return board

def initPawnAttacks():
    for i in range (64):
        whitePawnAttacks[i] = generateWhitePawnAttacks(i)
        blackPawnAttacks[i] = generateBlackPawnAttacks(i)

def getPawnAttacks(color, square):
    if color == WHITE:
        return whitePawnAttacks[square]
    elif color == BLACK:
        return blackPawnAttacks[square]
    else:
        raise ValueError("Invalid color")

def generateKnightAttacks(square):
    file = squareFile(square)
    rank = squareRank(square)
    board = BT()
    if isOnBoard(rank + 1, file + 2):
        board.setValue(square + 10)
    if isOnBoard(rank + 1, file - 2):
        board.setValue(square + 6)
    if isOnBoard(rank - 1, file + 2):
        board.setValue(square - 6)
    if isOnBoard(rank - 1, file - 2):
        board.setValue(square - 10)
    if isOnBoard(rank + 2, file + 1):
        board.setValue(square + 17)
    if isOnBoard(rank + 2, file -1):
        board.setValue(square + 15)
    if isOnBoard(rank - 2, file + 1):
        board.setValue(square - 15)
    if isOnBoard(rank - 2, file - 1):
        board.setValue(square - 17)
    return board

def initKnightAttacks():
    for i in range (64):
        knightAttacks[i] = generateKnightAttacks(i)

def getKnightAttacks(square):
    return knightAttacks[square]

def generateKingAttacks(square):
    file = squareFile(square)
    rank = squareRank(square)
    board = BT()
    if isOnBoard(rank + 1, file + 1):
        board.setValue(square + 9)
    if isOnBoard(rank + 1, file):
        board.setValue(square + 8)
    if isOnBoard(rank + 1, file - 1):
        board.setValue(square + 7)
    if isOnBoard(rank, file + 1):
        board.setValue(square + 1)
    if isOnBoard(rank, file - 1):
        board.setValue(square - 1)
    if isOnBoard(rank - 1, file + 1):
        board.setValue(square - 7)
    if isOnBoard(rank - 1, file):
        board.setValue(square - 8)
    if isOnBoard(rank - 1, file - 1):
        board.setValue(square - 9)
    return board

def initKingAttacks():
    for i in range (64):
        kingAttacks[i] = generateKingAttacks(i)

def getKingAttacks(square):
    return kingAttacks[square]

def generateBishopMask(square):
    board = BT()
    temporaryPos = square
    while isOnBoard(squareRank(temporaryPos) + 1, squareFile(temporaryPos) + 1):
        temporaryPos += 9
        board.setValue(temporaryPos)
    temporaryPos = square
    while isOnBoard(squareRank(temporaryPos) - 1, squareFile(temporaryPos) - 1):
        temporaryPos -= 9
        board.setValue(temporaryPos)
    temporaryPos = square
    while isOnBoard(squareRank(temporaryPos) - 1, squareFile(temporaryPos) + 1):
        temporaryPos -= 7
        board.setValue(temporaryPos)
    temporaryPos = square
    while isOnBoard(squareRank(temporaryPos) + 1, squareFile(temporaryPos) - 1):
        temporaryPos += 7
        board.setValue(temporaryPos)
    return board

def getBishopMask(square):
    return bishopMasks[square]

def initBishopMasks():
    for i in range (64):
        bishopMasks[i] = generateBishopMask(i)

def generateBishopAttacks(square, blockers):
    board = BT()
    temporaryPos = square
    while isOnBoard(squareRank(temporaryPos) + 1, squareFile(temporaryPos) + 1):
        temporaryPos += 9
        board.setValue(temporaryPos)
        if blockers.checkValue(temporaryPos):
            break
    temporaryPos = square
    while isOnBoard(squareRank(temporaryPos) - 1, squareFile(temporaryPos) - 1):
        temporaryPos -= 9
        board.setValue(temporaryPos)
        if blockers.checkValue(temporaryPos):
            break
    temporaryPos = square
    while isOnBoard(squareRank(temporaryPos) - 1, squareFile(temporaryPos) + 1):
        temporaryPos -= 7
        board.setValue(temporaryPos)
        if blockers.checkValue(temporaryPos):
            break
    temporaryPos = square
    while isOnBoard(squareRank(temporaryPos) + 1, squareFile(temporaryPos) - 1):
        temporaryPos += 7
        board.setValue(temporaryPos)
        if blockers.checkValue(temporaryPos):
            break
    return board

def getBishopAttacks(square, blockers):
    return generateBishopAttacks(square, blockers)

def generateRookMask(square):
    board = BT()
    temporaryPos = square
    while isOnBoard(squareRank(temporaryPos), squareFile(temporaryPos) + 1):
        temporaryPos += 1
        board.setValue(temporaryPos)
    temporaryPos = square
    while isOnBoard(squareRank(temporaryPos), squareFile(temporaryPos) - 1):
        temporaryPos -= 1
        board.setValue(temporaryPos)
    temporaryPos = square
    while isOnBoard(squareRank(temporaryPos) + 1, squareFile(temporaryPos)):
        temporaryPos += 8
        board.setValue(temporaryPos)
    temporaryPos = square
    while isOnBoard(squareRank(temporaryPos) - 1, squareFile(temporaryPos)):
        temporaryPos -= 8
        board.setValue(temporaryPos)
    return board

def initRookMasks():
    for i in range (64):
        rookMasks[i] = generateRookMask(i)

def getRookMask(square):
    return rookMasks[square]

def generateRookAttacks(square, blockers):
    board = BT()
    temporaryPos = square
    while isOnBoard(squareRank(temporaryPos), squareFile(temporaryPos) + 1):
        temporaryPos += 1
        board.setValue(temporaryPos)
        if blockers.checkValue(temporaryPos):
            break
    temporaryPos = square
    while isOnBoard(squareRank(temporaryPos), squareFile(temporaryPos) - 1):
        temporaryPos -= 1
        board.setValue(temporaryPos)
        if blockers.checkValue(temporaryPos):
            break
    temporaryPos = square
    while isOnBoard(squareRank(temporaryPos) + 1, squareFile(temporaryPos)):
        temporaryPos += 8
        board.setValue(temporaryPos)
        if blockers.checkValue(temporaryPos):
            break
    temporaryPos = square
    while isOnBoard(squareRank(temporaryPos) - 1, squareFile(temporaryPos)):
        temporaryPos -= 8
        board.setValue(temporaryPos)
        if blockers.checkValue(temporaryPos):
            break
    return board

def getRookAttacks(square, blockers):
    return generateRookAttacks(square, blockers)

def generateQueenAttacks(square, blockers):
    board = BT()
    temporaryPos = square
    while isOnBoard(squareRank(temporaryPos), squareFile(temporaryPos) + 1):
        temporaryPos += 1
        board.setValue(temporaryPos)
        if blockers.checkValue(temporaryPos):
            break
    temporaryPos = square
    while isOnBoard(squareRank(temporaryPos), squareFile(temporaryPos) - 1):
        temporaryPos -= 1
        board.setValue(temporaryPos)
        if blockers.checkValue(temporaryPos):
            break
    temporaryPos = square
    while isOnBoard(squareRank(temporaryPos) + 1, squareFile(temporaryPos)):
        temporaryPos += 8
        board.setValue(temporaryPos)
        if blockers.checkValue(temporaryPos):
            break
    temporaryPos = square
    while isOnBoard(squareRank(temporaryPos) - 1, squareFile(temporaryPos)):
        temporaryPos -= 8
        board.setValue(temporaryPos)
        if blockers.checkValue(temporaryPos):
            break
    temporaryPos = square
    while isOnBoard(squareRank(temporaryPos) + 1, squareFile(temporaryPos) + 1):
        temporaryPos += 9
        board.setValue(temporaryPos)
        if blockers.checkValue(temporaryPos):
            break
    temporaryPos = square
    while isOnBoard(squareRank(temporaryPos) - 1, squareFile(temporaryPos) - 1):
        temporaryPos -= 9
        board.setValue(temporaryPos)
        if blockers.checkValue(temporaryPos):
            break
    temporaryPos = square
    while isOnBoard(squareRank(temporaryPos) - 1, squareFile(temporaryPos) + 1):
        temporaryPos -= 7
        board.setValue(temporaryPos)
        if blockers.checkValue(temporaryPos):
            break
    temporaryPos = square
    while isOnBoard(squareRank(temporaryPos) + 1, squareFile(temporaryPos) - 1):
        temporaryPos += 7
        board.setValue(temporaryPos)
        if blockers.checkValue(temporaryPos):
            break
    return board

def getQueenAttacks(square, blockers):
    return generateQueenAttacks(square, blockers)

def isSquareAttacked(position, square, color):
    if color == WHITE:
        pawnAttackers = blackPawnAttacks[square]
        if (pawnAttackers & position.getBitboard(WHITE, PAWN)).bitboard != 0:
            return True
    elif color == BLACK:
        pawnAttackers = whitePawnAttacks[square]
        if (pawnAttackers & position.getBitboard(BLACK, PAWN)).bitboard != 0:
            return True
    if (knightAttacks[square] & position.getBitboard(color, KNIGHT)).bitboard != 0:
        return True
    if (kingAttacks[square] & position.getBitboard(color, KING)).bitboard != 0:
        return True
    blockers = position.occupancy(BOTH)
    bishopAttacks = generateBishopAttacks(square, blockers)
    bishopAttackers = (
        position.getBitboard(color, BISHOP) |
        position.getBitboard(color, QUEEN)
    )
    if (bishopAttacks & bishopAttackers).bitboard != 0:
        return True
    rookAttacks = generateRookAttacks(square, blockers)
    rookAttackers = (
        position.getBitboard(color, ROOK) |
        position.getBitboard(color, QUEEN)
    )
    if (rookAttacks & rookAttackers).bitboard != 0:
        return True
    return False

def init():
    initPawnAttacks()
    initKnightAttacks()
    initKingAttacks()
    initBishopMasks()
    initRookMasks()