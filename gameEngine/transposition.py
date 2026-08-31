import sys
import os
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from constants import LOWER_BOUND, EXACT, UPPER_BOUND, NO_MATCH, NOT_DEEP_ENOUGH, USABLE, NOT_USABLE

class TTEntry():
    def __init__(self, hash, depth, score, flag, bestMove):
        self.hash = hash
        self.depth = depth
        self.score = score
        self.flag = flag
        self.bestMove = bestMove
    
def initTable():
    return {}

def storeEntry(table, hash, depth, score, flag, bestMove):
    entry = table.get(hash)
    # depth-preferred replacement: don't overwrite a deeper (more trustworthy)
    # result with a shallower one; ties get replaced with the newer result.
    if entry == None or entry.depth <= depth:
        table[hash] = TTEntry(hash, depth, score, flag, bestMove)

def probeEntry(table, hash, depth, alpha, beta):
    # Always returns a (status, payload) tuple so callers can safely do
    # `status, payload = probeEntry(...)` regardless of which branch fires.
    entry = table.get(hash)
    if entry == None:
        return (NO_MATCH, None)
    elif entry.depth < depth:
        # Too shallow to trust the score, but still hand back the move
        # for move ordering.
        return (NOT_DEEP_ENOUGH, entry.bestMove)
    else:
        if entry.flag == EXACT:
            return (USABLE, entry.score)
        elif entry.flag == LOWER_BOUND and entry.score >= beta:
            return (USABLE, entry.score)
        elif entry.flag == UPPER_BOUND and entry.score <= alpha:
            return (USABLE, entry.score)
        else:
            return (NOT_USABLE, entry.bestMove)

def probeMove(table, hash):
    entry = table.get(hash)
    if entry != None:
        return entry.bestMove
    else:
        return None

def clearTable(table):
    table.clear()

