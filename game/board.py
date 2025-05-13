import numpy as np
from typing import List, Tuple

class Board:
    def __init__(self, rows: int = 6, columns: int = 7):
        self.rows = rows
        self.columns = columns
        self.grid = np.zeros((rows, columns), dtype=int)
        self.current_player = 1
        self.winner = 0
        self.is_game_over = False

    def copy(self) -> 'Board':
        new_board = Board(self.rows, self.columns)
        new_board.grid = self.grid.copy()
        new_board.current_player = self.current_player
        new_board.winner = self.winner
        new_board.is_game_over = self.is_game_over
        return new_board

    def drop_piece(self, column: int) -> bool:
        if not self.is_valid_move(column):
            return False

        for row in range(self.rows-1, -1, -1):
            if self.grid[row][column] == 0:
                self.grid[row][column] = self.current_player
                if self.check_win(row, column):
                    self.winner = self.current_player
                    self.is_game_over = True
                elif self.is_draw():
                    self.is_game_over = True
                else:
                    self.current_player = 3 - self.current_player
                return True
        return False

    def is_valid_move(self, column: int) -> bool:
        return 0 <= column < self.columns and self.grid[0][column] == 0

    def get_legal_moves(self) -> List[int]:
        return [col for col in range(self.columns) if self.is_valid_move(col)]

    def check_win(self, row: int, col: int) -> bool:
        player = self.grid[row][col]
        directions = [
            [(0, 1), (0, -1)],  # Horizontal
            [(1, 0), (-1, 0)],   # Vertical
            [(1, 1), (-1, -1)],  # Diagonal /
            [(1, -1), (-1, 1)]   # Diagonal \
        ]

        for direction_pair in directions:
            count = 1
            for dr, dc in direction_pair:
                r, c = row + dr, col + dc
                while 0 <= r < self.rows and 0 <= c < self.columns:
                    if self.grid[r][c] == player:
                        count += 1
                        r += dr
                        c += dc
                    else:
                        break
            if count >= 4:
                return True
        return False

    def is_draw(self) -> bool:
        return all(self.grid[0][col] != 0 for col in range(self.columns))

    def evaluate_position(self, player: int) -> float:
        score = 0
        opponent = 3 - player
        
        # Avalia todas as possíveis sequências de 4 células
        for r in range(self.rows):
            for c in range(self.columns):
                # Verifica horizontal
                if c <= self.columns - 4:
                    segment = [self.grid[r][c+i] for i in range(4)]
                    score += self.evaluate_segment(segment, player, opponent)
                # Verifica vertical
                if r <= self.rows - 4:
                    segment = [self.grid[r+i][c] for i in range(4)]
                    score += self.evaluate_segment(segment, player, opponent)
                # Verifica diagonal ascendente
                if r <= self.rows - 4 and c <= self.columns - 4:
                    segment = [self.grid[r+i][c+i] for i in range(4)]
                    score += self.evaluate_segment(segment, player, opponent)
                # Verifica diagonal descendente
                if r >= 3 and c <= self.columns - 4:
                    segment = [self.grid[r-i][c+i] for i in range(4)]
                    score += self.evaluate_segment(segment, player, opponent)
        
        return score

    def evaluate_segment(self, segment: List[int], player: int, opponent: int) -> float:
        player_count = segment.count(player)
        opponent_count = segment.count(opponent)
        
        if player_count == 4:
            return 100
        if opponent_count == 4:
            return -100
        
        if player_count == 3 and opponent_count == 0:
            return 5
        if player_count == 2 and opponent_count == 0:
            return 2
        if player_count == 1 and opponent_count == 0:
            return 1
        
        if opponent_count == 3 and player_count == 0:
            return -5
        if opponent_count == 2 and player_count == 0:
            return -2
        if opponent_count == 1 and player_count == 0:
            return -1
        
        return 0

    def to_feature_vector(self) -> List[int]:
        features = []
        # Adiciona o estado do tabuleiro
        features.extend(self.grid.flatten().tolist())
        # Adiciona características estratégicas
        features.append(self.current_player)
        features.append(self.evaluate_position(1))
        features.append(self.evaluate_position(2))
        return features