import pygame
import sys
from typing import Optional
from game.board import Board  

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
        self.width = Board.COLS * self.SQUARESIZE 
        self.height = (Board.ROWS + 1) * self.SQUARESIZE 
        self.size = (self.width + 1, self.height + 1)

        pygame.init()
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption("Connect Four")

        self.title_font = pygame.font.SysFont("Courier New", 70, bold=True)
        self.button_font = pygame.font.SysFont("Courier New", 40, bold=True)
        self.game_font = pygame.font.SysFont("Courier New", 75, bold=True)
        self.info_font = pygame.font.SysFont("Courier New", 24, bold=True)

        self.animation_speed = 5

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
                piece = board.state[row][col]
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

        turn_text = self.button_font.render(
            f"Player {board.current_player}'s turn",
            True,
            self.PLAYER1_COLOR if board.current_player == 1 else self.PLAYER2_COLOR
        )
        self.screen.blit(turn_text, (20, 20))

        player1_text = self.info_font.render("Player 1", True, self.PLAYER1_COLOR)
        player2_text = self.info_font.render("Player 2", True, self.PLAYER2_COLOR)
        self.screen.blit(player1_text, (self.width - 200, 20))
        self.screen.blit(player2_text, (self.width - 200, 50))
        pygame.draw.circle(self.screen, self.PLAYER1_COLOR, (self.width - 250, 30), 10)
        pygame.draw.circle(self.screen, self.PLAYER2_COLOR, (self.width - 250, 60), 10)

        pygame.display.update()

    def animate_piece_drop(self, board: Board, col: int, row: int):
        x_pos = col * self.SQUARESIZE + self.SQUARESIZE // 2
        color = self.PLAYER1_COLOR if board.current_player == 1 else self.PLAYER2_COLOR

        for y in range(0, (row + 1) * self.SQUARESIZE + self.SQUARESIZE // 2, self.animation_speed):
            self.draw_board(board)
            pygame.draw.circle(self.screen, color, (x_pos, y), self.RADIUS)
            pygame.display.update()
            pygame.time.delay(10)

    def get_human_move(self, board: Board) -> int:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos[0]
                    col = pos // self.SQUARESIZE
                    if board.is_valid_move(col):
                        return col

            pos = pygame.mouse.get_pos()[0]
            if 0 <= pos < self.width:
                self.draw_board(board)
                color = self.PLAYER1_COLOR if board.current_player == 1 else self.PLAYER2_COLOR
                temp_circle = pygame.Surface((self.RADIUS * 2, self.RADIUS * 2), pygame.SRCALPHA)
                transparent_color = (*color, 128)  
                pygame.draw.circle(temp_circle, transparent_color, (self.RADIUS, self.RADIUS), self.RADIUS)
                self.screen.blit(temp_circle, (pos - self.RADIUS, self.SQUARESIZE // 2 - self.RADIUS))
                pygame.display.update()

    def show_game_over(self, winner: Optional[int]):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        if winner:
            text = f"Player {winner} wins!"
            color = self.PLAYER1_COLOR if winner == 1 else self.PLAYER2_COLOR
        else:
            text = "It's a draw!"
            color = self.TEXT_COLOR

        label = self.game_font.render(text, True, color)
        self.screen.blit(label, (self.width // 2 - label.get_width() // 2,
                                 self.height // 2 - label.get_height() // 2))

        pygame.display.update()
        pygame.time.wait(3000)
