## Pieces object
An object containing:
- The piece name (string)
- The piece number position (int)
- The piece character position (string)

## Player
An object containing:
* The player color (bool)
* The pieces possessed (string list)
* The pieces taken to the adversary (string list)
* The score (int)
* The time (int)
* Can castle (bool)

## Cell object
An object containing:
* If the cell is passable or not
## Global data
A list containing:
* Both players (lists)
* The active player (bool)
* Has anyone won (bool)
* The grid (list of list of objects cell)