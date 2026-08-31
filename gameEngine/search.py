import os
import sys
import time

sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gameCore'))

from constants import (
    INFINITY, MATE_SCORE,
    EXACT, LOWER_BOUND, UPPER_BOUND,
    NOT_DEEP_ENOUGH, USABLE, NOT_USABLE,
    PIECE_VALUES,
)
from moveGenerator import generateLegalMoves, colorOf, applyMove, isInCheck
from zorbrist import computeHash, updateHashMove
from transposition import initTable, storeEntry, probeEntry, probeMove, clearTable
from evaluate import evaluate as classicalEvaluate

table = initTable()
lastEvalFn = None


def ensureFreshTable(evalFn):
    global lastEvalFn
    if evalFn is not lastEvalFn:
        clearTable(table)
        lastEvalFn = evalFn


def moveScore(position, move, ttMove):
    if ttMove is not None and move == ttMove:
        return 1_000_000
    if move.isCapture():
        attackerColor, attackerPiece = position.getPiece(move.start)
        if move.isEnPassant():
            victimValue = PIECE_VALUES[0]
        else:
            victimColor, victimPiece = position.getPiece(move.end)
            victimValue = PIECE_VALUES[victimPiece]
        return 100_000 + victimValue - PIECE_VALUES[attackerPiece]
    return 0


def orderMoves(position, moves, ttMove):
    moves.sort(key=lambda move: moveScore(position, move, ttMove), reverse=True)


def quiescenceSearch(position, alpha, beta, evalFn):
    standPat = evalFn(position)
    if standPat >= beta:
        return beta
    alpha = max(alpha, standPat)

    color = colorOf(position)
    captureMoves = [m for m in generateLegalMoves(position, color) if m.isCapture()]
    orderMoves(position, captureMoves, ttMove=None)

    for move in captureMoves:
        newPosition = position.copy()
        applyMove(newPosition, move)
        score = -quiescenceSearch(newPosition, -beta, -alpha, evalFn)
        if score >= beta:
            return beta
        alpha = max(alpha, score)

    return alpha


def negamax(position, depth, alpha, beta, ply, hash, evalFn):
    originalAlpha = alpha

    status, payload = probeEntry(table, hash, depth, alpha, beta)
    ttMove = None
    if status == USABLE:
        return payload
    if status in (NOT_DEEP_ENOUGH, NOT_USABLE):
        ttMove = payload

    if depth == 0:
        return quiescenceSearch(position, alpha, beta, evalFn)

    color = colorOf(position)
    moves = generateLegalMoves(position, color)

    if not moves:
        return -MATE_SCORE + ply if isInCheck(position, color) else 0

    orderMoves(position, moves, ttMove)

    bestScore = -INFINITY
    bestMove = None

    for move in moves:
        newPosition = position.copy()
        applyMove(newPosition, move)
        newHash = updateHashMove(hash, move, position, newPosition)

        score = -negamax(newPosition, depth - 1, -beta, -alpha, ply + 1, newHash, evalFn)

        if score > bestScore:
            bestScore = score
            bestMove = move
        alpha = max(alpha, score)
        if alpha >= beta:
            break

    if bestScore <= originalAlpha:
        flag = UPPER_BOUND
    elif bestScore >= beta:
        flag = LOWER_BOUND
    else:
        flag = EXACT

    storeEntry(table, hash, depth, bestScore, flag, bestMove)
    return bestScore


def iterativeDeepening(position, maxDepth, timeLimit, evalFn, verbose=True):
    startTime = time.time()
    rootHash = computeHash(position)

    bestMove = None
    bestScore = 0

    for depth in range(1, maxDepth + 1):
        if time.time() - startTime > timeLimit:
            break

        score = negamax(position, depth, -INFINITY, INFINITY, 0, rootHash, evalFn)

        move = probeMove(table, rootHash)
        if move is not None:
            bestMove = move
            bestScore = score

        if verbose:
            print(f"depth {depth}  score {score}  move {bestMove}  time {time.time() - startTime:.2f}s")

    return bestMove, bestScore


def search(position, timeLimit=5.0, maxDepth=64, evalFn=None, verbose=True):
    evalFn = evalFn or classicalEvaluate
    ensureFreshTable(evalFn)
    bestMove, bestScore = iterativeDeepening(position, maxDepth, timeLimit, evalFn, verbose)
    return bestMove
