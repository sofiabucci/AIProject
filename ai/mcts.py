import math
import random
from typing import Optional
from game.board import Board

class MCTSNode:
    def __init__(self, board: Board, parent: Optional['MCTSNode'] = None, 
                 move: Optional[int] = None):
        self.board = board.copy()
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.wins = 0.0
        self.untried_moves = board.get_legal_moves()
    
    def uct_value(self, exploration: float = 1.41) -> float:
        if self.visits == 0:
            return float('inf')
        return (self.wins / self.visits) + exploration * math.sqrt(math.log(self.parent.visits) / self.visits)
    
    def select_child(self) -> 'MCTSNode':
        return max(self.children, key=lambda child: child.uct_value())
    
    def expand(self) -> 'MCTSNode':
        move = random.choice(self.untried_moves)
        new_board = self.board.copy()
        new_board.drop_piece(move)
        child = MCTSNode(new_board, self, move)
        self.untried_moves.remove(move)
        self.children.append(child)
        return child
    
    def simulate(self) -> float:
        sim_board = self.board.copy()
        current_player = sim_board.current_player  # jogador a ser avaliado

        while not sim_board.is_game_over:
            legal_moves = sim_board.get_legal_moves()
            if not legal_moves:
                break

            # Heurística simples: escolher colunas mais próximas do centro
            move = sorted(legal_moves, key=lambda x: abs(x - sim_board.width // 2))[0]
            sim_board.drop_piece(move)

        if sim_board.winner == current_player:
            return 1.0
        elif sim_board.winner == 0:
            return 0.5
        return 0.0
    
    def backpropagate(self, result: float):
        self.visits += 1
        self.wins += result
        if self.parent:
            self.parent.backpropagate(1.0 - result)

class MCTSAgent:
    def __init__(self, iterations: int = 1000, exploration: float = 1.41):
        self.iterations = iterations
        self.exploration = exploration
    
    def get_best_move(self, board: Board) -> int:
        root = MCTSNode(board)
        
        for _ in range(self.iterations):
            node = root
            # Selection
            while not node.untried_moves and node.children:
                node = node.select_child()
            
            # Expansion
            if node.untried_moves:
                node = node.expand()
            
            # Simulation
            result = node.simulate()
            
            # Backpropagation
            node.backpropagate(result)
        
        return max(root.children, key=lambda c: c.visits).move
