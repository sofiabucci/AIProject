from typing import List, Optional

class Board:
    ROWS = 6
    COLS = 7
    WIN_LENGTH = 4
    
    def __init__(self, state: Optional[List[List[int]]] = None):
        self.state = state or [[0 for _ in range(self.COLS)] for _ in range(self.ROWS)]
    
    def drop_piece(self, col: int, player: int) -> bool:
        """Tenta colocar uma peça na coluna especificada"""
        for row in range(self.ROWS-1, -1, -1):
            if self.state[row][col] == 0:
                self.state[row][col] = player
                return True
        return False
    
    def is_valid_move(self, col: int) -> bool:
        """Verifica se um movimento é válido"""
        return 0 <= col < self.COLS and self.state[0][col] == 0
    
    def check_winner(self) -> Optional[int]:
        """Verifica se há um vencedor"""
        # Implementação da lógica de vitória (similar à won_game original)
        for row in range(self.ROWS):
            for col in range(self.COLS):
                player = self.state[row][col]
                if player == 0:
                    continue
                
                # Horizontal
                if col <= self.COLS - self.WIN_LENGTH:
                    if all(self.state[row][col+i] == player for i in range(self.WIN_LENGTH)):
                        return player
                
                # Vertical
                if row <= self.ROWS - self.WIN_LENGTH:
                    if all(self.state[row+i][col] == player for i in range(self.WIN_LENGTH)):
                        return player
                
                # Diagonal (descendente)
                if (row <= self.ROWS - self.WIN_LENGTH and 
                    col <= self.COLS - self.WIN_LENGTH):
                    if all(self.state[row+i][col+i] == player for i in range(self.WIN_LENGTH)):
                        return player
                
                # Diagonal (ascendente)
                if (row >= self.WIN_LENGTH - 1 and 
                    col <= self.COLS - self.WIN_LENGTH):
                    if all(self.state[row-i][col+i] == player for i in range(self.WIN_LENGTH)):
                        return player
        
        # Verifica empate
        if all(cell != 0 for row in self.state for cell in row):
            return 0
        
        return None
    
    def get_legal_moves(self) -> List[int]:
        """Retorna todas as colunas com movimentos válidos"""
        return [col for col in range(self.COLS) if self.is_valid_move(col)]
    
    def copy(self) -> 'Board':
        """Retorna uma cópia do tabuleiro"""
        return Board([row[:] for row in self.state])
    
    def __str__(self) -> str:
        """Representação visual do tabuleiro"""
        symbols = {0: ' ', 1: 'X', 2: 'O'}
        board_str = ""
        for row in self.state:
            board_str += "|" + "|".join(symbols[cell] for cell in row) + "|\n"
            board_str += "-" * (self.COLS * 2 + 1) + "\n"
        board_str += " " + " ".join(str(i) for i in range(self.COLS)) + "\n"
        return board_str