from constants import *
from bitboard import Bitboard as BT
from attacks import (
    squareRank, squareFile, makeSquare,
    knightAttacks, kingAttacks,
    getBishopAttacks, getRookAttacks, getQueenAttacks,
    isSquareAttacked,
)
from move import Move


def colorOf(position):
    return WHITE if position.sideToMove == 0 else BLACK


def opponentOf(color):
    return BLACK if color == WHITE else WHITE


def iterateSquares(bitboard):
    value = bitboard.bitboard
    while value:
        lsb = value & -value
        square = lsb.bit_length() - 1
        yield square
        value ^= lsb


def addPawnMove(moves, fromSquare, toSquare, isCapture, color):
    promotionRank = 7 if color == WHITE else 0
    if squareRank(toSquare) == promotionRank:
        tag = PROMOTION_CAPTURE if isCapture else PROMOTION
        for piece in (QUEEN, ROOK, BISHOP, KNIGHT):
            moves.append(Move(fromSquare, toSquare, tag, piece))
    else:
        tag = CAPTURE if isCapture else QUIET
        moves.append(Move(fromSquare, toSquare, tag))


def generatePawnMoves(position, moves, color):
    pawns = position.getBitboard(color, PAWN)
    empty = position.occupancy(EMPTY)
    enemy = position.occupancy(opponentOf(color))
    forward = 8 if color == WHITE else -8
    startRank = 1 if color == WHITE else 6

    for fromSquare in iterateSquares(pawns):
        rank = squareRank(fromSquare)
        file = squareFile(fromSquare)

        toSquare = fromSquare + forward
        if 0 <= toSquare <= 63 and empty.checkValue(toSquare):
            addPawnMove(moves, fromSquare, toSquare, False, color)
            if rank == startRank:
                doubleSquare = fromSquare + 2 * forward
                if empty.checkValue(doubleSquare):
                    moves.append(Move(fromSquare, doubleSquare, DOUBLE_PAWN_PUSH))

        for fileOffset in (-1, 1):
            targetFile = file + fileOffset
            if not (0 <= targetFile <= 7):
                continue
            targetSquare = fromSquare + forward + fileOffset
            if not (0 <= targetSquare <= 63):
                continue
            if enemy.checkValue(targetSquare):
                addPawnMove(moves, fromSquare, targetSquare, True, color)
            elif position.enPassant != -1 and targetSquare == position.enPassant:
                moves.append(Move(fromSquare, targetSquare, EN_PASSANT))


def generateStepMoves(position, moves, color, piece, attackTable):
    pieces = position.getBitboard(color, piece)
    own = position.occupancy(color)
    enemy = position.occupancy(opponentOf(color))

    for fromSquare in iterateSquares(pieces):
        targets = attackTable[fromSquare] & ~own
        for toSquare in iterateSquares(targets):
            tag = CAPTURE if enemy.checkValue(toSquare) else QUIET
            moves.append(Move(fromSquare, toSquare, tag))


def generateSlidingMoves(position, moves, color, piece):
    pieces = position.getBitboard(color, piece)
    own = position.occupancy(color)
    enemy = position.occupancy(opponentOf(color))
    blockers = position.occupancy(BOTH)

    for fromSquare in iterateSquares(pieces):
        if piece == BISHOP:
            attacked = getBishopAttacks(fromSquare, blockers)
        elif piece == ROOK:
            attacked = getRookAttacks(fromSquare, blockers)
        else:
            attacked = getQueenAttacks(fromSquare, blockers)

        targets = attacked & ~own
        for toSquare in iterateSquares(targets):
            tag = CAPTURE if enemy.checkValue(toSquare) else QUIET
            moves.append(Move(fromSquare, toSquare, tag))


def generateCastlingMoves(position, moves, color):
    opponent = opponentOf(color)

    if color == WHITE:
        kingStart, kingSideEnd, queenSideEnd = 4, 6, 2
        kingSideRight, queenSideRight = position.castlingRights[0], position.castlingRights[1]
        kingSideEmpty, queenSideEmpty = (5, 6), (1, 2, 3)
        kingSidePath, queenSidePath = (4, 5, 6), (4, 3, 2)
    else:
        kingStart, kingSideEnd, queenSideEnd = 60, 62, 58
        kingSideRight, queenSideRight = position.castlingRights[2], position.castlingRights[3]
        kingSideEmpty, queenSideEmpty = (61, 62), (57, 58, 59)
        kingSidePath, queenSidePath = (60, 61, 62), (60, 59, 58)

    if kingSideRight and all(position.isEmpty(sq) for sq in kingSideEmpty):
        if not any(isSquareAttacked(position, sq, opponent) for sq in kingSidePath):
            moves.append(Move(kingStart, kingSideEnd, KING_CASTLE))

    if queenSideRight and all(position.isEmpty(sq) for sq in queenSideEmpty):
        if not any(isSquareAttacked(position, sq, opponent) for sq in queenSidePath):
            moves.append(Move(kingStart, queenSideEnd, QUEEN_CASTLE))


def generatePseudoLegalMoves(position, color):
    moves = []

    generatePawnMoves(position, moves, color)
    generateStepMoves(position, moves, color, KNIGHT, knightAttacks)
    generateStepMoves(position, moves, color, KING, kingAttacks)
    generateSlidingMoves(position, moves, color, BISHOP)
    generateSlidingMoves(position, moves, color, ROOK)
    generateSlidingMoves(position, moves, color, QUEEN)
    generateCastlingMoves(position, moves, color)

    return moves


# squares whose departure or arrival should revoke castling rights
CASTLE_CLEAR = {
    4: (0, 1), 0: (1,), 7: (0,),
    60: (2, 3), 56: (3,), 63: (2,),
}


def clearCastlingRights(position, square):
    for index in CASTLE_CLEAR.get(square, ()):
        position.castlingRights[index] = False


def applyMove(position, move):
    color = colorOf(position)
    piece = position.getPieceType(move.start)
    wasPawnOrCapture = (piece == PAWN) or move.isCapture()

    position.enPassant = -1

    if move.isKingsideCastle() or move.isQueensideCastle():
        position.movePiece(move.start, move.end)
        if move.isKingsideCastle():
            rookStart, rookEnd = move.start + 3, move.start + 1
        else:
            rookStart, rookEnd = move.start - 4, move.start - 1
        position.movePiece(rookStart, rookEnd)
    elif move.isEnPassant():
        capturedSquare = move.end - 8 if color == WHITE else move.end + 8
        position.removePiece(capturedSquare)
        position.movePiece(move.start, move.end)
    else:
        position.movePiece(move.start, move.end)
        if move.isPromoting():
            position.replacePiece(move.end, color, move.promotionPiece())
        elif move.isDoublePawnPush():
            position.enPassant = (move.start + move.end) // 2

    clearCastlingRights(position, move.start)
    clearCastlingRights(position, move.end)

    position.halfmoveClock = 0 if wasPawnOrCapture else position.halfmoveClock + 1
    if color == BLACK:
        position.fullmoveClock += 1

    position.sideToMove = 1 - position.sideToMove


def isInCheck(position, color):
    kingSquare = position.kingSquare(color)
    if kingSquare is None:
        return False
    return isSquareAttacked(position, kingSquare, opponentOf(color))


def generateLegalMoves(position, color):
    legalMoves = []
    for move in generatePseudoLegalMoves(position, color):
        testPosition = position.copy()
        applyMove(testPosition, move)
        if not isInCheck(testPosition, color):
            legalMoves.append(move)
    return legalMoves


def generateMoves(position):
    return generateLegalMoves(position, colorOf(position))