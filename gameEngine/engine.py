import os
import sys

sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gameCore'))

from search import search
from evaluate import evaluate as classicalEvaluate


class Engine:
    def __init__(self, evalFn=None, timeLimit=5.0, maxDepth=64, verbose=True):
        self.evalFn = evalFn or classicalEvaluate
        self.timeLimit = timeLimit
        self.maxDepth = maxDepth
        self.verbose = verbose

    def findBestMove(self, position, timeLimit=None, maxDepth=None):
        return search(
            position,
            timeLimit=timeLimit if timeLimit is not None else self.timeLimit,
            maxDepth=maxDepth if maxDepth is not None else self.maxDepth,
            evalFn=self.evalFn,
            verbose=self.verbose,
        )
