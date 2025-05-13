class Board:
    def __init__(self, rows: int = 6, columns: int = 7):
        self.rows = rows
        self.columns = columns
        self.grid = [[0 for _ in range(columns)] for _ in range(rows)]
        self.current_player = 1
        self.last_move = None  # Armazena a última jogada (row, col)
        self.winner = None
        self.is_game_over = False

    def copy(self) -> 'Board':
        new_board = Board(self.rows, self.columns)
        new_board.grid = [row[:] for row in self.grid]
        new_board.current_player = self.current_player
        new_board.last_move = self.last_move
        new_board.winner = self.winner
        new_board.is_game_over = self.is_game_over
        return new_board

    def drop_piece(self, column: int) -> tuple:
        """Insere uma peça na coluna especificada e retorna (row, col)"""
        if column < 0 or column >= self.columns:
            raise ValueError("Coluna inválida")
            
        for row in reversed(range(self.rows)):
            if self.grid[row][column] == 0:
                self.grid[row][column] = self.current_player
                self.last_move = (row, column)
                
                # Verifica vitória
                if self.check_win():
                    self.winner = self.current_player
                    self.is_game_over = True
                
                # Verifica empate
                elif all(self.grid[0][col] != 0 for col in range(self.columns)):
                    self.is_game_over = True
                
                return row, column
        raise ValueError("Coluna cheia")

    def check_win(self, row: int = None, col: int = None) -> bool:
        """Verifica se há um vencedor a partir da última jogada ou das coordenadas especificadas"""
        if row is None or col is None:
            if self.last_move is None:
                return False
            row, col = self.last_move

        player = self.grid[row][col]
        if player == 0:
            return False

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

    def is_valid_move(self, column: int) -> bool:
        """Verifica se um movimento é válido"""
        return 0 <= column < self.columns and self.grid[0][column] == 0

    def get_legal_moves(self) -> list:
        """Retorna todas as colunas com movimentos válidos"""
        return [col for col in range(self.columns) if self.is_valid_move(col)]

    def count_connected(self, player: int, length: int) -> int:
        """Conta sequências de 'length' peças conectadas para o jogador"""
        count = 0
        # Verifica horizontal
        for row in range(self.rows):
            for col in range(self.columns - length + 1):
                if all(self.grid[row][col+i] == player for i in range(length)):
                    count += 1
        # Verifica vertical
        for row in range(self.rows - length + 1):
            for col in range(self.columns):
                if all(self.grid[row+i][col] == player for i in range(length)):
                    count += 1
        # Verifica diagonal /
        for row in range(self.rows - length + 1):
            for col in range(self.columns - length + 1):
                if all(self.grid[row+i][col+i] == player for i in range(length)):
                    count += 1
        # Verifica diagonal \
        for row in range(length - 1, self.rows):
            for col in range(self.columns - length + 1):
                if all(self.grid[row-i][col+i] == player for i in range(length)):
                    count += 1
        return count

    def simulate_move(self, column: int) -> 'Board':
        """Cria uma cópia do tabuleiro com o movimento simulado"""
        new_board = self.copy()
        new_board.drop_piece(column)
        new_board.current_player = 3 - self.current_player  # Alterna jogador
        return new_board

    def to_feature_vector(self) -> list:
        """Converte o tabuleiro para um vetor de features"""
        features = []
        for row in self.grid:
            features.extend(row)
        features.append(self.current_player)
        return features