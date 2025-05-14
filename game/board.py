from typing import List, Optional, Tuple
import numpy as np

class Board:
    ROWS = 6
    COLS = 7
    WIN_LENGTH = 4
    
    def __init__(self, state: Optional[List[List[int]]] = None):
        self.state = state or [[0 for _ in range(self.COLS)] for _ in range(self.ROWS)]
        self._current_player = 1
        self._winner = None
        self._game_over = False
        self._last_move = None

    def __lt__(self, other):
        """Implement less-than for heapq comparisons"""
        # We don't actually care about the comparison, just need to define it
        return id(self) < id(other)

    @property
    def current_player(self) -> int:
        return self._current_player

    @property
    def last_move(self) -> Optional[Tuple[int, int]]:
        return self._last_move

    def drop_piece(self, col: int) -> bool:
        if self._game_over or not self.is_valid_move(col):
            return False
            
        for row in range(self.ROWS-1, -1, -1):
            if self.state[row][col] == 0:
                self.state[row][col] = self._current_player
                self._last_move = (row, col)
                
                if self._check_winner(row, col):
                    self._winner = self._current_player
                    self._game_over = True
                elif self._is_full():
                    self._game_over = True
                else:
                    self._current_player = 3 - self._current_player
                return True
        return False

    def is_valid_move(self, col: int) -> bool:
        return 0 <= col < self.COLS and self.state[0][col] == 0

    def _check_winner(self, row: int, col: int) -> bool:
        directions = [
            (0, 1),  # Horizontal
            (1, 0),  # Vertical
            (1, 1),  # Diagonal /
            (1, -1)  # Diagonal \
        ]
        player = self.state[row][col]
        
        for dr, dc in directions:
            count = 1
            for direction in [1, -1]:
                r, c = row + dr * direction, col + dc * direction
                while 0 <= r < self.ROWS and 0 <= c < self.COLS and self.state[r][c] == player:
                    count += 1
                    r += dr * direction
                    c += dc * direction
                    if count >= self.WIN_LENGTH:
                        return True
        return False

    def is_winning_move(self, col: int, player: int) -> bool:
        """Check if dropping a piece in this column would win the game"""
        temp_board = self.copy()
        if temp_board.drop_piece(col):
            return temp_board.winner == player
        return False

    def _is_full(self) -> bool:
        return all(cell != 0 for cell in self.state[0])

    def get_legal_moves(self) -> List[int]:
        return [col for col in range(self.COLS) if self.is_valid_move(col)]

    def copy(self) -> 'Board':
        return Board([row[:] for row in self.state])

    def evaluate_position(self, player: int) -> float:
        """Simple position evaluation function"""
        score = 0
        opponent = 3 - player
        
        # Center column preference
        center_col = self.COLS // 2
        center_count = sum(self.state[r][center_col] == player for r in range(self.ROWS))
        score += center_count * 0.5
        
        # Check for potential wins
        for col in self.get_legal_moves():
            if self.is_winning_move(col, player):
                score += 100
            elif self.is_winning_move(col, opponent):
                score -= 80
                
        return score

    def to_numpy(self) -> np.ndarray:
        return np.array(self.state)
    
    def to_feature_vector(self, player_perspective: int = 1) -> List[float]:
        """Convert board state to feature vector for ML model"""
        features = []
        opponent = 3 - player_perspective
        
        # Flatten the board state from perspective player
        for row in self.state:
            for cell in row:
                if cell == player_perspective:
                    features.append(1.0)
                elif cell == opponent:
                    features.append(-1.0)
                else:
                    features.append(0.0)
        
        # Add current player indicator
        features.append(1.0 if self.current_player == player_perspective else -1.0)
        
        # Add pattern features (simplified)
        patterns = self._detect_patterns(player_perspective)
        features.extend(patterns)
        
        return features
    
    def _detect_patterns(self, player: int) -> List[float]:
        """Detect common patterns in the board"""
        opponent = 3 - player
        patterns = [0.0] * 8  # Simplified pattern detection
        
        # Check for potential wins
        for col in self.get_legal_moves():
            if self.is_winning_move(col, player):
                patterns[0] = 1.0  # Immediate win
            elif self.is_winning_move(col, opponent):
                patterns[1] = 1.0  # Block opponent win
        
        # Count potential lines
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            player_count, opp_count = self._count_lines(player, opponent, dr, dc)
            if player_count >= 3:
                patterns[2] += 0.5  # 3 in a line
            if opp_count >= 3:
                patterns[3] += 0.5
        
        return patterns
    
    def _count_lines(self, player: int, opponent: int, dr: int, dc: int) -> Tuple[int, int]:
        """Count potential lines for player and opponent"""
        player_lines = 0
        opp_lines = 0
        
        for r in range(self.ROWS):
            for c in range(self.COLS):
                if self.state[r][c] == 0:  # Empty cell
                    # Check player potential
                    if self._check_potential_line(r, c, player, dr, dc):
                        player_lines += 1
                    # Check opponent potential
                    if self._check_potential_line(r, c, opponent, dr, dc):
                        opp_lines += 1
        
        return player_lines, opp_lines
    
    def _check_potential_line(self, row: int, col: int, player: int, dr: int, dc: int) -> bool:
        """Check if this empty cell could complete a line for player"""
        count = 0
        for i in range(1, 4):
            r, c = row + dr * i, col + dc * i
            if 0 <= r < self.ROWS and 0 <= c < self.COLS:
                if self.state[r][c] == player:
                    count += 1
                elif self.state[r][c] != 0:
                    return False
        return count >= 2

    @property
    def is_game_over(self) -> bool:
        return self._game_over

    @property
    def winner(self) -> Optional[int]:
        return self._winner

    def __str__(self) -> str:
        symbols = {0: '.', 1: 'X', 2: 'O'}
        board_str = "\n" + "  ".join(str(i) for i in range(self.COLS)) + "\n"
        board_str += "-" * (2 * self.COLS + 1) + "\n"
        
        for row in self.state:
            board_str += "|" + "|".join(symbols[cell] for cell in row) + "|\n"
            board_str += "-" * (2 * self.COLS + 1) + "\n"
        return board_str