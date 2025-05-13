import math
import heapq
import pandas as pd
import random 
from typing import Optional
from game.board import Board
from ai.decision_tree import DecisionTree

class AStar:
    def __init__(self, board: Board, player: int, decision_tree: Optional[DecisionTree] = None):
        self.initial_board = board.copy()
        self.player = player
        self.opponent = 3 - player
        self.decision_tree = decision_tree
        self.transposition_table = {}

    def search(self, max_depth: int = 5) -> int:
        open_set = []
        initial_g = 0
        initial_h = self._evaluate(self.initial_board)
        heapq.heappush(open_set, (initial_g + initial_h, initial_g, self.initial_board, []))
        
        best_score = -math.inf
        best_action = None
        
        while open_set:
            current_f, current_g, current_board, action_path = heapq.heappop(open_set)
            
            if len(action_path) >= max_depth or current_board.is_game_over:
                current_score = self._evaluate(current_board)
                if current_score > best_score:
                    best_score = current_score
                    if action_path:
                        best_action = action_path[0]
                continue
            
            for move in current_board.get_legal_moves():
                new_board = current_board.copy()
                new_board.drop_piece(move)
                new_action_path = action_path + [move]
                new_g = current_g + 1
                new_h = self._evaluate(new_board)
                new_f = new_g + new_h
                
                heapq.heappush(open_set, (new_f, new_g, new_board, new_action_path))
        
        return best_action if best_action is not None else random.choice(self.initial_board.get_legal_moves())

    def _evaluate(self, board: Board) -> float:
        board_key = str(board.grid)
        if board_key in self.transposition_table:
            return self.transposition_table[board_key]
        
        if board.winner == self.player:
            score = 1000
        elif board.winner == self.opponent:
            score = -1000
        elif self.decision_tree:
            features = board.to_feature_vector()
            score = self.decision_tree.predict(pd.DataFrame([features]))[0]
        else:
            score = board.evaluate_position(self.player) - board.evaluate_position(self.opponent) * 1.2
        
        self.transposition_table[board_key] = score
        return score