import numpy as np
from game import constants as c
from dataclasses import dataclass, field

@dataclass
class Board:
    rows: int = c.ROWS
    columns: int = c.COLUMNS
    board: np.ndarray = field(default_factory=lambda: np.zeros((6,7)))
            
    def get_board(self) -> np.ndarray:
        return self.board

    def print_board(self) -> None:
        print(np.flip(self.board, 0), "\n")
        
 