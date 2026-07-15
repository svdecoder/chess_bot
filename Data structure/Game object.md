## 1. Move history
We will use an object to store all the different moves of the game:
```
moveHistory
|
└── History (list -> list)
    ├── Move 1 (list)
	    ├── Initial case (int)
	    ├── Final case (int)
	    ├── Move type (int - move nomenclature)
	    └── Piece promoted to (int - piece nomenclature)
    ├── Move 2 (list)
    ├── Move 3 (list)
    ├── ...
    └── Last move (list)
```
### A. Move nomenclature
This represent the position of the boolean representing the move flag:
```
Classic = 0
Capture = 1
En passant = 2
Castle = 3
Promotion = 4
Double pawn push = 5
```
e.i: 
* Simple move: `100000`
* En passant: `001000`
* Promotion + capture: `010010`


### B. Piece nomenclature
```
Queen = 0
Rook = 1
Knight = 2
Bishop = 3
```

## 2. Clock
We will use an object clock to store the clock of each player (rounded to the second up)
```
clock
|
├── White clock (int - time in second)
|   
└── Black clock (int - time in secod)
```

## 3. Game state
The game state represent each game. It is stored as an object:
```
gameState
|
├── clock
|
├── moveHistory
|   
├── position
|
└── result (int)
	├── 0 if white won
	├── 1 if black won
	├── 2 for a tie
	└── 3 if the game is still going
```
