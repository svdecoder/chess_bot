## 1. Explanation
According to the FEN, in order to recreate any chess position, we need  informations:
* **The piece placement** - handled by the bitboard
* The player turn
* The castling rights
* The en-passant move
* **An halfmove clock** - count the number of move since the last pawn move/capture (for the 50 move rule)
* **Fullmove number** – starts at 1 and is incremented after each Black move 

## 2. Data structure
We are going to use an object to store all those data:
```
Position 
│ 
├── White (list -> int)
│   ├── Pawns (int)
│   ├── Knights (int)
│   ├── Bishops (int)
│   ├── Rooks (int)
│   ├── Queens (int)
│   └── King (int)
│ 
├── Black (list -> int)
│   ├── Pawns (int)
│   ├── Knights (int)
│   ├── Bishops (int)
│   ├── Rooks (int)
│   ├── Queens (int)
│   └── King (int)
│ 
├── Side to move (bool)
|   ├── White = 0
|   └── Black = 1
|
├── Castling rights (list -> bool)
|   ├── White kingside
|   ├── White queenside
|   ├── Black kingside
|   └── Black queenside
|
├── En passant square (int)
|   ├── -1 for None
|   └── 0 -> 63 for valid value 
|
├── Halfmove clock (int)
|
└── Fullmove number (int)
```
