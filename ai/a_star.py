import math
import heapq
import random
from typing import Optional, List, Dict
import numpy as np
import pandas as pd
from game.board import Board
from ai.decision_tree import DecisionTree

class AStar:
    def __init__(self, board: Board, player: int, decision_tree: Optional[DecisionTree] = None):
        self.initial_board = board.copy()
        self.player = player
        self.opponent = 3 - player
        self.decision_tree = decision_tree
        self.transposition_table: Dict[str, float] = {}
        self.node_count = 0
        self.max_depth = 5
        self.use_heuristic = True

    def search(self) -> int:
        """Executes A* search and returns the best move"""
        # Use a tuple with a unique counter to avoid comparing Board objects
        open_set = []
        heapq.heappush(open_set, (0, self.node_count, 0, self.initial_board, []))
        self.node_count += 1
        
        best_score = -math.inf
        best_move = None
        
        while open_set and self.node_count < 10000:
            current_f, _, current_g, current_board, path = heapq.heappop(open_set)

            if len(path) >= self.max_depth or current_board.is_game_over:
                current_score = self._evaluate(current_board)
                if current_score > best_score:
                    best_score = current_score
                    if path:
                        best_move = path[0]
                continue

            legal_moves = self._get_ordered_moves(current_board)
            
            for move in legal_moves:
                new_board = current_board.copy()
                new_board.drop_piece(move)
                new_path = path + [move]
                new_g = current_g + 1
                new_h = self._evaluate(new_board) if self.use_heuristic else 0
                new_f = new_g + new_h
                
                heapq.heappush(open_set, (new_f, self.node_count, new_g, new_board, new_path))
                self.node_count += 1

        return best_move if best_move is not None else self._fallback_move()

    def _get_ordered_moves(self, board: Board) -> List[int]:
        moves = board.get_legal_moves()
        
        if not self.use_heuristic:
            return moves
        
        scored_moves = []
        for move in moves:
            temp_board = board.copy()
            temp_board.drop_piece(move)
            score = self._evaluate(temp_board)
            scored_moves.append((score, move))
        
        scored_moves.sort(reverse=True, key=lambda x: x[0])
        return [move for (score, move) in scored_moves]

    def _evaluate(self, board: Board) -> float:
        board_key = str(board.state)
        
        if board_key in self.transposition_table:
            return self.transposition_table[board_key]
        
        if board.winner == self.player:
            return 1000
        if board.winner == self.opponent:
            return -1000
        
        if self.decision_tree:
            try:
                features = board.to_feature_vector(self.player)
                dt_score = self.decision_tree.predict(pd.DataFrame([features]))[0]
                normalized_score = dt_score * 1000
                self.transposition_table[board_key] = normalized_score
                return normalized_score
            except Exception:
                pass
        
        score = 0
        
        for r in range(board.ROWS):
            for c in range(board.COLS):
                if c <= board.COLS - 4:
                    segment = [board.state[r][c+i] for i in range(4)]
                    score += self._evaluate_segment(segment)
                if r <= board.ROWS - 4:
                    segment = [board.state[r+i][c] for i in range(4)]
                    score += self._evaluate_segment(segment)
                if r <= board.ROWS - 4 and c <= board.COLS - 4:
                    segment = [board.state[r+i][c+i] for i in range(4)]
                    score += self._evaluate_segment(segment)
                if r >= 3 and c <= board.COLS - 4:
                    segment = [board.state[r-i][c+i] for i in range(4)]
                    score += self._evaluate_segment(segment)
        
        center_col = board.COLS // 2
        for r in range(board.ROWS):
            if board.state[r][center_col] == self.player:
                score += 2
        
        self.transposition_table[board_key] = score
        return score

    def _evaluate_segment(self, segment: List[int]) -> float:
        player_count = segment.count(self.player)
        opponent_count = segment.count(self.opponent)
        
        if player_count == 4: return 100
        if opponent_count == 4: return -100
        if player_count == 3 and opponent_count == 0: return 50
        if player_count == 2 and opponent_count == 0: return 10
        if player_count == 1 and opponent_count == 0: return 1
        if opponent_count == 3 and player_count == 0: return -50
        if opponent_count == 2 and player_count == 0: return -10
        if opponent_count == 1 and player_count == 0: return -1
        return 0

    def _fallback_move(self) -> int:
        legal_moves = self.initial_board.get_legal_moves()
        if not legal_moves:
            raise ValueError("No legal moves available")
        
        center = self.initial_board.columns // 2
        if center in legal_moves:
            return center
        
        return random.choice(legal_moves)

class AStarAgent:
    def __init__(self, max_depth: int = 5, decision_tree: Optional[DecisionTree] = None):
        self.max_depth = max_depth
        self.decision_tree = decision_tree
    
    def get_best_move(self, board: Board) -> int:
        """Interface for the A* agent"""
        astar = AStar(board, board.current_player, self.decision_tree)
        astar.max_depth = self.max_depth
        return astar.search()