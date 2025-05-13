from typing import List, Optional, Tuple
import numpy as np

class Board:
    ROWS = 6
    COLS = 7
    WIN_LENGTH = 4
    
    def __init__(self, state: Optional[List[List[int]]] = None):
        """
        Inicializa o tabuleiro do Connect Four.
        
        Args:
            state: Estado inicial do tabuleiro (opcional)
        """
        self.state = state or [[0 for _ in range(self.COLS)] for _ in range(self.ROWS)]
        self._current_player = 1  # Jogador 1 começa
        self._winner = None
        self._game_over = False
        self._last_move = None  # Armazena a última jogada (row, col)

    @property
    def current_player(self) -> int:
        """Retorna o jogador atual (1 ou 2)"""
        return self._current_player

    @property
    def last_move(self) -> Optional[Tuple[int, int]]:
        """Retorna a última jogada (linha, coluna)"""
        return self._last_move

    def drop_piece(self, col: int) -> bool:
        """
        Tenta colocar uma peça na coluna especificada.
        
        Args:
            col: Coluna onde a peça será colocada (0-6)
            
        Returns:
            True se a jogada foi válida, False caso contrário
        """
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
                    self._current_player = 3 - self._current_player  # Alterna jogador
                return True
        return False

    def is_valid_move(self, col: int) -> bool:
        """Verifica se uma jogada na coluna é válida"""
        return 0 <= col < self.COLS and self.state[0][col] == 0
    

    def _check_winner(self, row: int, col: int) -> bool:
        """Verifica se a última jogada resultou em vitória"""
        directions = [
            (0, 1),  # Horizontal
            (1, 0),  # Vertical
            (1, 1),  # Diagonal /
            (1, -1)  # Diagonal \
        ]
        player = self.state[row][col]
        
        for dr, dc in directions:
            count = 1  # Conta a peça atual
            # Verifica em ambas as direções
            for direction in [1, -1]:
                r, c = row + dr * direction, col + dc * direction
                while 0 <= r < self.ROWS and 0 <= c < self.COLS and self.state[r][c] == player:
                    count += 1
                    r += dr * direction
                    c += dc * direction
                    if count >= self.WIN_LENGTH:
                        return True
        return False
    
    def count_connected(self, player: int) -> int:
        """
        Conta quantas sequências conectadas (>=2) o jogador possui.
        Pode ser usado para avaliação heurística.
        """
        count = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for row in range(self.ROWS):
            for col in range(self.COLS):
                if self.state[row][col] != player:
                    continue
                for dr, dc in directions:
                    seq_len = 1
                    r, c = row + dr, col + dc
                    while 0 <= r < self.ROWS and 0 <= c < self.COLS and self.state[r][c] == player:
                        seq_len += 1
                        r += dr
                        c += dc
                    if seq_len >= 2:
                        count += 1
        return count

    def _is_full(self) -> bool:
        """Verifica se o tabuleiro está completamente cheio"""
        return all(cell != 0 for cell in self.state[0])

    def get_legal_moves(self) -> List[int]:
        """Retorna uma lista de colunas com jogadas válidas"""
        moves = [col for col in range(self.COLS) if self.is_valid_move(col)]
        if not moves and not self._game_over:
            raise RuntimeError("Invalid game state - no moves but game not over")
        return moves

    def copy(self) -> 'Board':
        """Cria uma cópia profunda do tabuleiro"""
        return Board([row[:] for row in self.state])

    def to_feature_vector(self) -> List[int]:
        """Converte o estado do tabuleiro para um vetor 1D"""
        return [cell for row in self.state for cell in row]

    def to_numpy(self) -> np.ndarray:
        """Converte o tabuleiro para um array numpy"""
        return np.array(self.state)

    @property
    def is_game_over(self) -> bool:
        """Indica se o jogo terminou"""
        return self._game_over

    @property
    def winner(self) -> Optional[int]:
        """Retorna o vencedor (1, 2) ou None se empate/jogo em andamento"""
        return self._winner

    def __str__(self) -> str:
        """Representação visual do tabuleiro"""
        symbols = {0: '.', 1: 'X', 2: 'O'}
        board_str = "\n" + "  ".join(str(i) for i in range(self.COLS)) + "\n"
        board_str += "-" * (2 * self.COLS + 1) + "\n"
        
        for row in self.state:
            board_str += "|" + "|".join(symbols[cell] for cell in row) + "|\n"
            board_str += "-" * (2 * self.COLS + 1) + "\n"
        return board_str 