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
        self.max_depth = 5  # Profundidade máxima de busca
        self.use_heuristic = True  # Ativar/desativar heurística

    def search(self) -> int:
        """Executa a busca A* e retorna a melhor jogada"""
        open_set = []
        initial_g = 0
        initial_h = self._evaluate(self.initial_board)
        
        # (f_score, g_score, board, path)
        heapq.heappush(open_set, (initial_g + initial_h, initial_g, self.initial_board, []))
        
        best_score = -math.inf
        best_move = None
        
        while open_set and self.node_count < 10000:  # Limite de nós
            current_f, current_g, current_board, path = heapq.heappop(open_set)
            self.node_count += 1

            # Verifica se atingiu a profundidade máxima ou fim de jogo
            if len(path) >= self.max_depth or current_board.is_game_over:
                current_score = self._evaluate(current_board)
                if current_score > best_score:
                    best_score = current_score
                    if path:
                        best_move = path[0]
                continue

            # Gera os movimentos possíveis ordenados por heurística
            legal_moves = self._get_ordered_moves(current_board)
            
            for move in legal_moves:
                new_board = current_board.copy()
                new_board.drop_piece(move)
                new_path = path + [move]
                new_g = current_g + 1
                new_h = self._evaluate(new_board) if self.use_heuristic else 0
                new_f = new_g + new_h
                
                heapq.heappush(open_set, (new_f, new_g, new_board, new_path))

        return best_move if best_move is not None else self._fallback_move()

    def _get_ordered_moves(self, board: Board) -> List[int]:
        """Retorna movimentos ordenados por heurística (melhores primeiro)"""
        moves = board.get_legal_moves()
        
        if not self.use_heuristic:
            return moves
        
        # Avalia cada movimento com a heurística
        scored_moves = []
        for move in moves:
            temp_board = board.copy()
            temp_board.drop_piece(move)
            score = self._evaluate(temp_board)
            scored_moves.append((score, move))
        
        # Ordena do maior para o menor score
        scored_moves.sort(reverse=True, key=lambda x: x[0])
        return [move for (score, move) in scored_moves]

    def _evaluate(self, board: Board) -> float:
        """Função de avaliação que combina heurística personalizada e Decision Tree"""
        board_key = str(board.grid)
        
        # Verifica no cache
        if board_key in self.transposition_table:
            return self.transposition_table[board_key]
        
        # Verificação de vitória/derrota imediata
        if board.winner == self.player:
            return 1000
        if board.winner == self.opponent:
            return -1000
        
        # Usa Decision Tree se disponível
        if self.decision_tree:
            features = board.to_feature_vector()
            try:
                dt_score = self.decision_tree.predict(pd.DataFrame([features]))[0]
                return dt_score
            except:
                pass  # Fallback para heurística padrão
        
        # Heurística padrão
        score = 0
        
        # Avalia todas as linhas, colunas e diagonais
        for r in range(board.rows):
            for c in range(board.columns):
                # Horizontal
                if c <= board.columns - 4:
                    segment = [board.grid[r][c+i] for i in range(4)]
                    score += self._evaluate_segment(segment)
                # Vertical
                if r <= board.rows - 4:
                    segment = [board.grid[r+i][c] for i in range(4)]
                    score += self._evaluate_segment(segment)
                # Diagonal /
                if r <= board.rows - 4 and c <= board.columns - 4:
                    segment = [board.grid[r+i][c+i] for i in range(4)]
                    score += self._evaluate_segment(segment)
                # Diagonal \
                if r >= 3 and c <= board.columns - 4:
                    segment = [board.grid[r-i][c+i] for i in range(4)]
                    score += self._evaluate_segment(segment)
        
        # Bônus para peças centrais
        center_col = board.columns // 2
        for r in range(board.rows):
            if board.grid[r][center_col] == self.player:
                score += 2
        
        self.transposition_table[board_key] = score
        return score

    def _evaluate_segment(self, segment: List[int]) -> float:
        """Avalia um segmento de 4 células"""
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
        """Movimento de fallback quando a busca não encontra solução"""
        legal_moves = self.initial_board.get_legal_moves()
        if not legal_moves:
            raise ValueError("No legal moves available")
        
        # Prefere colunas centrais
        center = self.initial_board.columns // 2
        if center in legal_moves:
            return center
        
        return random.choice(legal_moves)

class AStarAgent:
    def __init__(self, max_depth: int = 5, decision_tree: Optional[DecisionTree] = None):
        self.max_depth = max_depth
        self.decision_tree = decision_tree
    
    def get_best_move(self, board: Board) -> int:
        """Interface para o agente A*"""
        astar = AStar(board, board.current_player, self.decision_tree)
        astar.max_depth = self.max_depth
        return astar.search()