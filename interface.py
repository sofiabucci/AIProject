import pygame 
import itertools
import sys
from game_rules import constants as c
from game_rules.board import Board
import game_rules.game_logic as game
from dataclasses import dataclass
from typing import Tuple, Optional

@dataclass
class Interface:
    rows: int = c.ROWS
    columns: int = c.COLUMNS
    square_size: int = c.SQUARESIZE
    width: int = c.WIDTH
    height: int = c.HEIGHT
    radius: float = c.RADIUS
    size: Tuple[int, int] = (c.WIDTH, c.HEIGHT)
    screen: pygame.Surface = pygame.display.set_mode((c.WIDTH, c.HEIGHT))
    
    def __post_init__(self):
        """Initialize pygame and set caption after dataclass creation"""
        pygame.init()
        pygame.display.set_caption("Connect4")
        
        # Load fonts once at initialization
        self.title_font = pygame.font.Font("./fonts/04B_30__.TTF", 60)
        self.button_font = pygame.font.Font("./fonts/Minecraft.ttf", 25)
        self.result_font = pygame.font.SysFont("Monospace", 50, bold=True)

    def start_game(self, board: Board) -> None:
        """Set up the game conditions and start the game loop"""
        self.draw_options_screen()
        game_mode = self.get_game_mode()
        board.print_board()
        self.draw_board()    
        pygame.display.update()
        self.play_game(board, game_mode)

    def play_game(self, board: Board, game_mode: int) -> None:
        """Main game loop"""
        game_matrix = board.get_board()
        game_over = False
        turns = itertools.cycle([1, 2])  
        current_player = next(turns)
        
        while not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    self.quit()
                
                self.handle_mouse_motion(current_player)
                
                # Human move handling
                if event.type == pygame.MOUSEBUTTONDOWN:	
                    if current_player == 1 or (current_player == 2 and game_mode == 1):
                        if not self.process_human_move(board, game_matrix, current_player, event):
                            continue
                        if game.winning_move(game_matrix, current_player):
                            game_over = True
                            break
                        current_player = next(turns)
                
                # AI move handling
                if current_player != 1 and game_mode != 1: 
                    pygame.time.wait(15)
                    game_over = game.ai_move(board, self, game_mode, game_matrix, current_player)
                    if game_over: 
                        break
                    current_player = next(turns)
            
            if game.is_game_tied(game_matrix):
                self.show_result(None)  # Draw
                break

        if game.winning_move(game_matrix, current_player):
            self.show_result(current_player)
            
        pygame.time.wait(3000)  # Wait 3 seconds before closing

    def handle_mouse_motion(self, current_player: int) -> None:
        """Handle mouse motion to show piece preview"""
        pos = pygame.mouse.get_pos()
        if 0 <= pos[0] <= self.width and 0 <= pos[1] <= self.square_size:
            pygame.draw.rect(self.screen, c.BACKGROUND_COLOR, 
                            (0, 0, self.width, self.square_size-14))
            pygame.draw.circle(self.screen, c.PIECES_COLORS[current_player], 
                             (pos[0], int(self.square_size/2)-7), self.radius)
            pygame.display.update()

    def process_human_move(self, board: Board, game_matrix: list, 
                          player: int, event) -> bool:
        """Process human move and return if valid"""
        return game.human_move(board, self, game_matrix, player, event)

    def draw_options_screen(self) -> None:
        """Draw the initial options screen"""
        self.screen.fill(c.BACKGROUND_COLOR)
        self.draw_text("Connect 4", self.title_font, c.BUTTON_TEXT_COLOR, 
                      (self.width//2, 230))
        self.draw_button((self.width//2, self.height//2, 300, 50), 
                        "Player x Player")
        self.draw_button((self.width//2, self.height//2 + 100, 300, 50), 
                        "Single Player")

    def get_game_mode(self) -> int:
        """Get game mode from user selection"""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    self.quit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Check Player vs Player button
                    if self.is_button_clicked((self.width//2 - 150, 350, 300, 50), mouse_pos):
                        return 1
                    
                    # Check Player vs AI button
                    if self.is_button_clicked((self.width//2 - 150, 450, 300, 50), mouse_pos):
                        self.draw_ai_options()
                        return self.get_ai_difficulty()
            
            pygame.display.flip()

    def draw_ai_options(self) -> None:
        """Draw AI difficulty options screen"""
        self.screen.fill(c.BACKGROUND_COLOR)
        self.draw_button((self.width//2, 250, 300, 50), "Easy (A*)")
        self.draw_button((self.width//2, 350, 300, 50), "Medium (A* Adversarial)")
        self.draw_button((self.width//2, 450, 300, 50), "Hard (Alpha Beta)")
        self.draw_button((self.width//2, 550, 300, 50), "Expert (MCTS)")

    def get_ai_difficulty(self) -> int:
        """Get AI difficulty level from user selection"""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    self.quit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Map button positions to difficulty levels
                    difficulties = {
                        (self.width//2 - 150, 250, 300, 50): 2,  # Easy
                        (self.width//2 - 150, 350, 300, 50): 3,  # Medium
                        (self.width//2 - 150, 450, 300, 50): 4,  # Hard
                        (self.width//2 - 150, 550, 300, 50): 5   # Expert
                    }
                    
                    for button_rect, difficulty in difficulties.items():
                        if self.is_button_clicked(button_rect, mouse_pos):
                            return difficulty
            
            pygame.display.flip()

    def draw_board(self) -> None:
        """Draw the game board with empty slots"""
        self.screen.fill(c.BACKGROUND_COLOR)    

        # Draw board shadow and main board
        shadow_rect = (2*self.square_size-10, self.square_size-10, 
                      self.columns*self.square_size+24, self.rows*self.square_size+24)
        board_rect = (2*self.square_size-10, self.square_size-10, 
                     self.columns*self.square_size+20, self.rows*self.square_size+20)
        
        pygame.draw.rect(self.screen, c.SHADOW_COLOR, shadow_rect, 0, 30)
        pygame.draw.rect(self.screen, c.BOARD_COLOR, board_rect, 0, 30)

        # Draw empty slots
        for col in range(self.columns):
            for row in range(self.rows):
                center = (int((col+5/2)*self.square_size), 
                         int((row+3/2)*self.square_size))
                pygame.draw.circle(self.screen, c.BACKGROUND_COLOR, center, self.radius)
        
        pygame.display.update()     
            
    def draw_new_piece(self, row: int, col: int, player: int) -> None:
        """Draw a new game piece on the board"""
        center = (int(col*self.square_size + self.square_size/2), 
                 self.height - int(row*self.square_size + self.square_size/2))
        pygame.draw.circle(self.screen, c.PIECES_COLORS[player], center, self.radius)
        pygame.display.update()

    def draw_button(self, rect: Tuple[int, int, int, int], text: str) -> None:
        """Draw a button with shadow and text"""
        x, y, width, height = rect
        shadow_rect = (x - 150, y, width, height)  # Adjusted for centering
        
        # Draw shadow and button
        pygame.draw.rect(self.screen, c.SHADOW_COLOR, shadow_rect, 0, 30)
        pygame.draw.rect(self.screen, c.BOARD_COLOR, (x - 150, y, width - 4, height - 4), 0, 30)
        
        # Draw button text
        self.draw_text(text, self.button_font, c.BUTTON_TEXT_COLOR, 
                     (x, y + height//2))

    def draw_text(self, text: str, font: pygame.font.Font, 
                color: Tuple[int, int, int], position: Tuple[int, int]) -> None:
        """Helper method to draw centered text"""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=position)
        self.screen.blit(text_surface, text_rect)

    def is_button_clicked(self, rect: Tuple[int, int, int, int], 
                        pos: Tuple[int, int]) -> bool:
        """Check if a position is within a button's rectangle"""
        x, y, width, height = rect
        return (x <= pos[0] <= x + width and 
                y <= pos[1] <= y + height)

    def show_result(self, winner: Optional[int]) -> None:
        """Show game result (winner or draw)"""
        if winner:
            label = self.result_font.render(f"Player {winner} wins!", True, 
                                          c.PIECES_COLORS[winner])
        else:
            label = self.result_font.render("Game tied!", True, c.BOARD_COLOR)
        
        self.screen.blit(label, (self.width//2 - label.get_width()//2, 15))
        pygame.display.update()

    @staticmethod
    def quit() -> None:
        """Cleanly exit the game"""
        pygame.quit()
        sys.exit()