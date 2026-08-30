from position import *

class GameState:
    def __init__(self, gameMode):
        self.clock = [gameMode[0], gameMode[0]]
        self.additionalTime = gameMode[1]

        self.moveHistory = []

        self.position = Position()
        self.result = 3