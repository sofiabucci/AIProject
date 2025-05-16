from game.board import Board
from ai.decision_tree import DecisionTree
from typing import Optional
import math
import random
import pandas as pd


class MCTSNode:
    def __init__(self, board: Board, parent: Optional['MCTSNode'] = None, 
                 move: Optional[int] = None, decision_tree: Optional[DecisionTree] = None):
        self.board = board.copy()
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.wins = 0.0
        self.untried_moves = board.get_legal_moves()
        self.decision_tree = decision_tree
    
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
        child = MCTSNode(new_board, self, move, self.decision_tree)
        self.untried_moves.remove(move)
        self.children.append(child)
        return child
    
    def simulate(self) -> float:
        sim_board = self.board.copy()
        current_player = sim_board.current_player

        while not sim_board.is_game_over:
            legal_moves = sim_board.get_legal_moves()
            if not legal_moves:
                break

            if self.decision_tree:
                # Use decision tree to evaluate moves
                scored_moves = []
                for move in legal_moves:
                    temp_board = sim_board.copy()
                    temp_board.drop_piece(move)
                    features = temp_board.to_feature_vector(current_player)
                    score = self.decision_tree.predict(pd.DataFrame([features]))[0]
                    scored_moves.append((score, move))
                
                # Choose move with highest score
                #scored_moves.sort(reverse=True, key=lambda x: x[0])
                move = max(scored_moves, key=lambda s,m: s + self._evaluate_move(sim_board,m,current_player))
            else:
                # Fallback to heuristic
                move = max(legal_moves, key=lambda m: self._evaluate_move(sim_board, m, current_player))
            
            sim_board.drop_piece(move)

        if sim_board.winner == current_player:
            return 1.0
        elif sim_board.winner == 0:
            return 0.5
        return 0.0
    
    def _evaluate_move(self, board: Board, move: int, player: int) -> float:
        temp_board = board.copy()
        temp_board.drop_piece(move)
        
        if temp_board.winner == player:
            return float('inf')
        
        opponent = 3 - player
        for opp_move in temp_board.get_legal_moves():
            if temp_board.is_winning_move(opp_move, opponent):
                return float('-inf')
        
        return temp_board.evaluate_position(player)
    
    def backpropagate(self, result: float):
        self.visits += 1
        self.wins += result
        if self.parent:
            self.parent.backpropagate(1.0 - result)

class MCTSAgent:
    def __init__(self, iterations: int = 1000, exploration: float = 1.41, 
                 decision_tree: Optional[DecisionTree] = None):
        self.iterations = iterations
        self.exploration = exploration
        self.decision_tree = decision_tree
    
    def get_best_move(self, board: Board) -> int:
        root = MCTSNode(board, decision_tree=self.decision_tree)
        
        for _ in range(self.iterations):
            node = root
            while not node.untried_moves and node.children:
                node = node.select_child()
            
            if node.untried_moves:
                node = node.expand()
            
            result = node.simulate()
            node.backpropagate(result)
        
        return max(root.children, key=lambda c: c.visits).move