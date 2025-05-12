import math
import random
from typing import Optional
from game.board import Board
from game.interface import GraphicalInterface

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
        current_player = sim_board.current_player  # Jogador a ser avaliado

        while not sim_board.is_game_over:
            legal_moves = sim_board.get_legal_moves()
            if not legal_moves:
                break

            # Avaliação heurística dos movimentos
            def evaluate_move(move):
                temp_board = sim_board.copy()
                temp_board.drop_piece(move)

                # Priorizar vitória imediata
                if temp_board.winner == current_player:
                    return float('inf')

                # Bloquear vitória do adversário
                for i in range(0,6) :
                    board_adv = temp_board.copy()
                    board_adv.drop_piece(i)
                    # GraphicalInterface.draw_board(board_adv);
                    if board_adv.winner != 0 and board_adv.winner != current_player:
                        return float('-inf')
                    

                # Maximizar conectividade (valoriza peças agrupadas)
                return temp_board.count_connected(current_player, 3) + 2 * temp_board.count_connected(current_player, 4)

            # Escolher o melhor movimento com base na heurística
            move = max(legal_moves, key=evaluate_move)
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
        
        return max(root.children, key=lambda c: c.wins / c.visits).move
