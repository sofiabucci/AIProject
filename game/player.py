from typing import Optional
from abc import ABC, abstractmethod

class Player(ABC):
    """
    Abstract base class for all players
    """
    def __init__(self, player_id: int):
        self.player_id = player_id
    
    @abstractmethod
    def get_move(self, board) -> int:
        pass
    
    def __str__(self):
        return f"Player {self.player_id} ({self.__class__.__name__})"

class HumanPlayer(Player):
    """
    Human player that takes input from console
    """
    def get_move(self, board) -> int:
        while True:
            try:
                col = int(input(f"Player {self.player_id}, enter column (0-{board.COLS-1}): "))
                if board.is_valid_move(col):
                    return col
                print("Invalid move. Try again.")
            except ValueError:
                print("Please enter a valid number.")

class AIPlayer(Player):
    """
    AI player that uses specified agent
    """
    def __init__(self, player_id: int, agent):
        super().__init__(player_id)
        self.agent = agent
    
    def get_move(self, board) -> int:
        move = self.agent.get_best_move(board)
        if not board.is_valid_move(move):
            raise ValueError(f"Agente sugeriu jogada inválida: {move}")
        return move

    
    def __str__(self):
        return f"AI Player {self.player_id} ({self.agent.__class__.__name__})"