import math
import random
from typing import Optional
import pandas as pd
from game.board import Board
from ai.decision_tree import DecisionTreeAgent

class MCTSNode:
    def __init__(self, board: Board, parent: Optional['MCTSNode'] = None, 
                 move: Optional[int] = None, decision_tree_agent: Optional[DecisionTreeAgent] = None):
        self.board = board.copy()
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.wins = 0.0
        self.untried_moves = board.get_legal_moves()
        self.decision_tree_agent = decision_tree_agent
    
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
        child = MCTSNode(new_board, self, move, self.decision_tree_agent)
        self.untried_moves.remove(move)
        self.children.append(child)
        return child
    
    def simulate(self) -> float:
        if self.decision_tree_agent:
            # Use Decision Tree to evaluate the position
            features = pd.DataFrame([self.board.to_feature_vector()])
            score = self.decision_tree_agent.model.predict(features)[0]
            
            # Normalize score to [0, 1] range
            max_score = 1000  # Assuming this is the max score from DecisionTree
            normalized_score = (score + max_score) / (2 * max_score)
            return normalized_score
        else:
            # Fallback to original simulation if no DecisionTree
            sim_board = self.board.copy()
            current_player = sim_board.current_player

            while not sim_board.is_game_over:
                legal_moves = sim_board.get_legal_moves()
                if not legal_moves:
                    break
                move = random.choice(legal_moves)
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
    def __init__(self, iterations: int = 1000, exploration: float = 1.41, 
                 decision_tree_agent: Optional[DecisionTreeAgent] = None):
        self.iterations = iterations
        self.exploration = exploration
        self.decision_tree_agent = decision_tree_agent
    
    def get_best_move(self, board: Board) -> int:
        root = MCTSNode(board, decision_tree_agent=self.decision_tree_agent)
        
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