FULL_BOARD = (1 << 64) - 1

def createMask(square):
    return 1 << square

class Bitboard:
    def __init__(self, bitboard = 0):
        self.bitboard = bitboard & FULL_BOARD

    def checkValue(self, squareToCheck):
        binsquareToCheck = createMask(squareToCheck)
        return (self.bitboard & binsquareToCheck) != 0

    def setValue(self, squareToSet):
        binsquareToSet = createMask(squareToSet)
        self.bitboard |= binsquareToSet
        return self.bitboard

    def clearValue(self, squareToClear):
        binsquareToClear = createMask(squareToClear)
        self.bitboard &= ~binsquareToClear
        return self.bitboard

    def toggleValue(self, squareToToggle):
        binsquareToToggle = createMask(squareToToggle)
        self.bitboard ^= binsquareToToggle
        return self.bitboard

    def countValue(self):
        return self.bitboard.bit_count()

    def positionLSB(self):
        board = self.bitboard
        if board == 0:
            return None
        return (board & -board).bit_length() - 1

    def popLSB(self):
        square = self.positionLSB()
        if square is not None:
            self.clearValue(square)
        return square

    def isEmpty(self):
        return self.bitboard == 0

    def _asInt(self, other):
        return other.bitboard if isinstance(other, Bitboard) else other

    def __and__(self, other):
        return Bitboard(self.bitboard & self._asInt(other))

    def __or__(self, other):
        return Bitboard(self.bitboard | self._asInt(other))

    def __xor__(self, other):
        return Bitboard(self.bitboard ^ self._asInt(other))

    def __invert__(self):
        return Bitboard(~self.bitboard & FULL_BOARD)

    def __lshift__(self, n):
        return Bitboard((self.bitboard << n) & FULL_BOARD)

    def __rshift__(self, n):
        return Bitboard(self.bitboard >> n)

    def __eq__(self, other):
        return self.bitboard == self._asInt(other)

    def __bool__(self):
        return self.bitboard != 0

    def __repr__(self):
        return f"Bitboard({self.bitboard:064b})"