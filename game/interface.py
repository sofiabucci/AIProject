import pygame
import sys
import time
from typing import Optional
from game.board import Board
from ai.mcts import MCTSAgent
from ai.a_star import AStar

class GraphicalInterface:
    def __init__(self):
        # Cores modernas
        self.BACKGROUND = (18, 18, 29)
        self.BOARD_COLOR = (39, 42, 68)
        self.SLOT_COLOR = (24, 26, 44)
        self.PLAYER1_COLOR = (234, 67, 53)
        self.PLAYER2_COLOR = (251, 188, 5)
        self.TEXT_COLOR = (255, 255, 255)
        self.ACCENT_COLOR = (88, 101, 242)
        self.BUTTON_COLOR = (88, 101, 242)
        self.BUTTON_HOVER = (50, 50, 150)
        self.BUTTON_SELECTED = (60, 70, 180)

        self.SQUARESIZE = 100
        self.RADIUS = int(self.SQUARESIZE / 2 - 10)
        self.width = Board.COLS * (self.SQUARESIZE + 1) 
        self.height = (Board.ROWS + 1) * (self.SQUARESIZE + 1)
        self.size = (self.width + 1, self.height + 1)

        pygame.init()
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption("Connect Four")

        self.title_font = pygame.font.SysFont("Courier New", 70, bold=True)
        self.button_font = pygame.font.SysFont("Courier New", 40, bold=True)
        self.game_font = pygame.font.SysFont("Courier New", 75, bold=True)
        self.info_font = pygame.font.SysFont("Courier New", 24, bold=True)

        self.animation_speed = 5
        self.game_mode = None
        self.board = Board()
        self.mcts_agent = MCTSAgent(iterations=1000)
        self.astar_agent = None
        self.ai_delay = 500  # ms entre jogadas no modo bot vs bot

    def draw_menu(self):
        self.screen.fill(self.BACKGROUND)
        title = self.title_font.render("CONNECT FOUR", True, self.ACCENT_COLOR)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))

        buttons = [
            {"text": "Player vs Player", "rect": pygame.Rect(0, 0, 500, 60), "mode": 1},
            {"text": "Player vs MCTS", "rect": pygame.Rect(0, 0, 500, 60), "mode": 2},
            {"text": "MCTS vs A*", "rect": pygame.Rect(0, 0, 500, 60), "mode": 3},
        ]

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]

        for i, button in enumerate(buttons):
            button["rect"].center = (self.width // 2, 220 + i * 100)
            is_hovered = button["rect"].collidepoint(mouse_pos)
            color = self.BUTTON_COLOR
            if is_hovered:
                color = self.BUTTON_HOVER
                if mouse_click:
                    color = self.BUTTON_SELECTED
            pygame.draw.rect(self.screen, color, button["rect"], border_radius=30)
            text = self.button_font.render(button["text"], True, self.TEXT_COLOR)
            self.screen.blit(text, (button["rect"].centerx - text.get_width() // 2,
                                    button["rect"].centery - text.get_height() // 2))

        footer = self.info_font.render("© 2025 Connect Four", True, (100, 100, 120))
        self.screen.blit(footer, (self.width // 2 - footer.get_width() // 2, self.height - 60))

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
                            # Efeito de clique
                            pygame.draw.rect(self.screen, (200, 200, 255), button["rect"], border_radius=10)
                            pygame.display.update(button["rect"])
                            pygame.time.delay(100)
                            return button["mode"]



    def draw_board(self):
        self.screen.fill(self.BACKGROUND)
        board_rect = pygame.Rect(0, self.SQUARESIZE, self.width, self.height - self.SQUARESIZE)
        pygame.draw.rect(self.screen, self.BOARD_COLOR, board_rect, border_radius=10)

        for col in range(Board.COLS):
            for row in range(Board.ROWS):
                pygame.draw.circle(self.screen, self.SLOT_COLOR,
                                 (col * self.SQUARESIZE + self.SQUARESIZE // 2,
                                  (row + 1) * self.SQUARESIZE + self.SQUARESIZE // 2),
                                 self.RADIUS + 2)
                pygame.draw.circle(self.screen, self.BOARD_COLOR,
                                 (col * self.SQUARESIZE + self.SQUARESIZE // 2,
                                  (row + 1) * self.SQUARESIZE + self.SQUARESIZE // 2),
                                 self.RADIUS)

        for col in range(Board.COLS):
            for row in range(Board.ROWS):
                piece = self.board.state[row][col]
                if piece == 1:
                    color = self.PLAYER1_COLOR
                elif piece == 2:
                    color = self.PLAYER2_COLOR
                else:
                    continue
                pygame.draw.circle(self.screen, color,
                                 (col * self.SQUARESIZE + self.SQUARESIZE // 2,
                                  (row + 1) * self.SQUARESIZE + self.SQUARESIZE // 2),
                                 self.RADIUS)

        # Top bar
        info_rect = pygame.Rect(0, 0, self.width, self.SQUARESIZE)
        pygame.draw.rect(self.screen, (30, 32, 50), info_rect)

        if self.game_mode == 3:  # Modo bot vs bot
            turn_text = self.button_font.render(
                f"{'MCTS' if self.board.current_player == 1 else 'A*'} is thinking...",
                True,
                self.PLAYER1_COLOR if self.board.current_player == 1 else self.PLAYER2_COLOR
            )
        else:
            turn_text = self.button_font.render(
                f"Player {self.board.current_player}'s turn",
                True,
                self.PLAYER1_COLOR if self.board.current_player == 1 else self.PLAYER2_COLOR
            )
            
        self.screen.blit(turn_text, (20, 20))

        pygame.display.update()

    def animate_piece_drop(self, board: Board, col: int, row: int):
        x_pos = col * self.SQUARESIZE + self.SQUARESIZE // 2
        color = self.PLAYER1_COLOR if board.current_player == 1 else self.PLAYER2_COLOR

        for y in range(0, (row + 1) * self.SQUARESIZE + self.SQUARESIZE // 2, self.animation_speed):
            self.draw_board()
            pygame.draw.circle(self.screen, color, (x_pos, y), self.RADIUS)
            pygame.display.update()
            pygame.time.delay(10)

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

            # Mostra a peça flutuante com efeito de hover
            pos = pygame.mouse.get_pos()[0]
            if 0 <= pos < self.width:
                pygame.draw.rect(self.screen, (30, 32, 50), (0, 0, self.width, self.SQUARESIZE))
                
                # Desenha um indicador na coluna
                col_hover = int(pos // self.SQUARESIZE)
                indicator_x = col_hover * self.SQUARESIZE + self.SQUARESIZE // 2
                pygame.draw.circle(self.screen, (100, 100, 150, 150), (indicator_x, 30), 5)
                
                # Desenha a peça flutuante
                color = self.PLAYER1_COLOR if board.current_player == 1 else self.PLAYER2_COLOR
                pygame.draw.circle(self.screen, color, (pos, int(self.SQUARESIZE/2)), self.RADIUS)
                
                # Sombra da peça
                shadow_color = (180, 50, 40) if board.current_player == 1 else (200, 160, 0)
                pygame.draw.circle(self.screen, shadow_color, (pos + 2, int(self.SQUARESIZE/2) + 2), self.RADIUS)
            
            pygame.display.update()

    def show_game_over(self, winner: Optional[int]):
        """Mostra mensagem de fim de jogo com overlay"""
        # Cria uma superfície semi-transparente
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Preto com 70% de opacidade
        self.screen.blit(overlay, (0, 0))
        
        if winner:
            text = f"Jogador {winner} venceu!"
            color = self.PLAYER1_COLOR if winner == 1 else self.PLAYER2_COLOR
        else:
            text = "Empate!"
            color = self.TEXT_COLOR
        
        # Texto principal
        label = self.game_font.render(text, True, color)
        self.screen.blit(label, (self.width//2 - label.get_width()//2, 
                           self.height//2 - label.get_height()//2 - 50))
        
        # Texto secundário
        subtext = self.button_font.render("Clique para continuar", True, (200, 200, 200))
        self.screen.blit(subtext, (self.width//2 - subtext.get_width()//2, 
                              self.height//2 + 50))
        
        pygame.display.update()
        
        # Espera por clique ou 3 segundos
        waiting = True
        start_time = pygame.time.get_ticks()
        while waiting:
            current_time = pygame.time.get_ticks()
            if current_time - start_time > 3000:  # 3 segundos
                waiting = False
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False