## 1. Explanations
For this project, we are going to use a bitboard.
A bitboard is a way to represent a chess board and pieces using only binary integers.
Bitboard are good for:
* Speed - calculus on 64 bit integer are fast
* Bitwise operations - those operations are matching the chess logic
* Memory efficiency - only a few 8 bytes integers are used
* Botting - since they are low memory and high speed, computations of combinations are really fast

## 2. Square numbering
For this bitwise project, we are going to consider the following chart:
$$\begin{gather}
\begin{matrix}
h_{1} & \dots & h_{8} \\
\vdots & \ddots & \vdots \\
a_{1} & \dots & a_{8}
\end{matrix} \to \begin{matrix}
56 & \dots & 63 \\
\vdots & \ddots & \vdots \\
0 & \dots & 7
\end{matrix}
\end{gather}$$
Which will be represented as:
```
56 57 58 59 60 61 62 63 
48 49 50 51 52 53 54 55 
40 41 42 43 44 45 46 47 
32 33 34 35 36 37 38 39 
24 25 26 27 28 29 30 31 
16 17 18 19 20 21 22 23 
8  9  10 11 12 13 14 15 
0  1  2  3  4  5  6  7
```

## 3. Bitboard used
We are going to use a 1 bitboard for each type of piece of each color, effectively having a bitboard for:
- White pawns
- White knights
- White bishops
- White rooks
- White queens
- White king
- Black pawns
- Black knights
- Black bishops
- Black rooks
- Black queens
- Black king
