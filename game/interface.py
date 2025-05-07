import pygame
import sys
from typing import Tuple, Optional
from game.board import Board

class GraphicalInterface:
    def __init__(self):
        # Cores
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BLUE = (0, 0, 255)
        self.RED = (255, 0, 0)
        self.YELLOW = (255, 255, 0)
        self.GREEN = (0, 255, 0)
        self.GRAY = (200, 200, 200)
        
        # Configurações
        self.SQUARESIZE = 100
        self.RADIUS = int(self.SQUARESIZE/2 - 5)
        self.width = Board.COLS * self.SQUARESIZE
        self.height = (Board.ROWS + 1) * self.SQUARESIZE
        self.size = (self.width, self.height)
        
        # Inicialização
        pygame.init()
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption("Connect Four")
        self.title_font = pygame.font.SysFont("Arial", 50, bold=True)
        self.button_font = pygame.font.SysFont("Arial", 30)
        self.game_font = pygame.font.SysFont("Arial", 75)

    def draw_menu(self):
        """Desenha o menu principal com opções de jogo"""
        self.screen.fill(self.BLACK)
        
        # Título
        title = self.title_font.render("CONNECT FOUR", True, self.WHITE)
        self.screen.blit(title, (self.width//2 - title.get_width()//2, 50))
        
        # Botões
        buttons = [
            {"text": "Humano vs Humano", "rect": pygame.Rect(0, 0, 300, 50), "mode": 1},
            {"text": "Humano vs IA", "rect": pygame.Rect(0, 0, 300, 50), "mode": 2},
            {"text": "IA vs IA", "rect": pygame.Rect(0, 0, 300, 50), "mode": 3}
        ]
        
        for i, button in enumerate(buttons):
            button["rect"].center = (self.width//2, 200 + i*100)
            color = self.GREEN if button["rect"].collidepoint(pygame.mouse.get_pos()) else self.GRAY
            pygame.draw.rect(self.screen, color, button["rect"])
            pygame.draw.rect(self.screen, self.WHITE, button["rect"], 2)
            
            text = self.button_font.render(button["text"], True, self.BLACK)
            self.screen.blit(text, (button["rect"].centerx - text.get_width()//2, 
                            button["rect"].centery - text.get_height()//2))
        
        pygame.display.update()
        return buttons

    def get_game_mode(self) -> int:
        """Obtém o modo de jogo selecionado pelo usuário"""
        while True:
            buttons = self.draw_menu()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    for button in buttons:
                        if button["rect"].collidepoint(pos):
                            return button["mode"]

    def draw_board(self, board: Board):
        """Desenha o tabuleiro e as peças"""
        self.screen.fill(self.BLACK)
        
        # Desenha o tabuleiro vazio
        for col in range(Board.COLS):
            for row in range(Board.ROWS):
                pygame.draw.rect(self.screen, self.BLUE, 
                               (col*self.SQUARESIZE, (row+1)*self.SQUARESIZE, 
                                self.SQUARESIZE, self.SQUARESIZE))
                pygame.draw.circle(self.screen, self.BLACK, 
                                 (int(col*self.SQUARESIZE+self.SQUARESIZE/2), 
                                  int((row+1)*self.SQUARESIZE+self.SQUARESIZE/2)), 
                                  self.RADIUS)
        
        # Desenha as peças
        for col in range(Board.COLS):
            for row in range(Board.ROWS):
                if board.state[row][col] == 1:
                    pygame.draw.circle(self.screen, self.RED, 
                                     (int(col*self.SQUARESIZE+self.SQUARESIZE/2), 
                                      self.height-int((row+0.5)*self.SQUARESIZE)), 
                                      self.RADIUS)
                elif board.state[row][col] == 2:
                    pygame.draw.circle(self.screen, self.YELLOW, 
                                     (int(col*self.SQUARESIZE+self.SQUARESIZE/2), 
                                      self.height-int((row+0.5)*self.SQUARESIZE)), 
                                      self.RADIUS)
        
        # Mostra de quem é a vez
        turn_text = self.button_font.render(
            f"Vez do Jogador {board.current_player}", 
            True, 
            self.RED if board.current_player == 1 else self.YELLOW
        )
        self.screen.blit(turn_text, (10, 10))
        
        pygame.display.update()

    def get_human_move(self, board: Board) -> int:
        """Obtém o movimento do jogador humano"""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos[0]
                    col = int(pos // self.SQUARESIZE)
                    if board.is_valid_move(col):
                        return col

            # Mostra a peça flutuante
            pos = pygame.mouse.get_pos()[0]
            if 0 <= pos < self.width:
                pygame.draw.rect(self.screen, self.BLACK, (0, 0, self.width, self.SQUARESIZE))
                pygame.draw.circle(
                    self.screen, 
                    self.RED if board.current_player == 1 else self.YELLOW,
                    (pos, int(self.SQUARESIZE/2)), 
                    self.RADIUS
                )
            pygame.display.update()

    def show_game_over(self, winner: Optional[int]):
        """Mostra mensagem de fim de jogo"""
        if winner:
            text = f"Jogador {winner} venceu!"
            color = self.RED if winner == 1 else self.YELLOW
        else:
            text = "Empate!"
            color = self.WHITE
        
        label = self.game_font.render(text, True, color)
        self.screen.blit(label, (self.width//2 - label.get_width()//2, 
                            self.height//2 - label.get_height()//2))
        pygame.display.update()
        pygame.time.wait(3000)