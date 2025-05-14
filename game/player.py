from typing import Optional
from abc import ABC, abstractmethod
from ai.decision_tree import DecisionTree

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
    def __init__(self, player_id: int, agent, decision_tree: Optional[DecisionTree] = None):
        super().__init__(player_id)
        self.agent = agent
        self.decision_tree = decision_tree
        if hasattr(agent, 'decision_tree'):
            agent.decision_tree = decision_tree
    
    def get_move(self, board) -> int:
        if self.decision_tree and hasattr(self.agent, 'decision_tree'):
            self.agent.decision_tree = self.decision_tree
        
        move = self.agent.get_best_move(board)
        if not board.is_valid_move(move):
            raise ValueError(f"Agent suggested invalid move: {move}")
        return move