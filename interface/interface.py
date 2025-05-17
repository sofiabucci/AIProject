import pygame 
import itertools
import sys
from game import constants as c
from game.board import Board
import game.rules as game
from dataclasses import dataclass


@dataclass
class Interface:
    rows: int = c.ROWS
    columns: int = c.COLUMNS
    pixels: int = c.SQUARESIZE
    width: int = c.WIDTH
    height: int = c.HEIGHT
    rad: float = c.RADIUS
    size: tuple = (width, height)
    screen: any = pygame.display.set_mode(size)
    pygame.display.set_caption("Connect4")


    def start_game(self, bd: Board) -> None:
        """Set up the conditions to the game, as choose game_mode and draw the pygame display"""
        pygame.init()
        self.draw_options_board()
        game_mode = self.choose_option()
        bd.print_board()	
        self.draw_board()    
        pygame.display.update()
        self.play_game(bd, game_mode)


    def play_game(self, bd: Board, game_mode: int) -> None:
        """Run the game"""
        board = bd.get_board()	
        game_over = False
        myfont = pygame.font.SysFont("Monospace", 50, bold=True)
        turns = itertools.cycle([1, 2])  
        turn = next(turns)
        
        while not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    self.quit()

                # Only show piece preview and accept human input in modes 1 and 2
                if game_mode != 3:
                    if event.type == pygame.MOUSEMOTION:
                        pygame.draw.rect(self.screen, c.BACKGROUND_COLOR, (0,0, self.width, self.pixels-14))
                        posx = event.pos[0]
                        pygame.draw.circle(self.screen, c.PIECES_COLORS[turn], (posx, int(self.pixels/2)-7), self.rad)
                        pygame.display.update()

                    # Human move (only in modes 1 and 2)
                    if event.type == pygame.MOUSEBUTTONDOWN and (turn == 1 or (turn == 2 and game_mode == 1)):
                        if not game.human_move(bd, self, board, turn, event): 
                            continue
                        if game.winning_move(board, turn): 
                            game_over = True
                            break
                        turn = next(turns)

            # AI moves
            if (game_mode == 2 and turn == 2) or game_mode == 3:
                pygame.time.wait(500)  # Add slight delay so we can see the moves
                game_over = game.ai_move(bd, self, game_mode, board, turn)
                if game_over: 
                    break
                turn = next(turns)

            if game.is_game_tied(board):
                self.show_draw(myfont)
                break

        if game.winning_move(board, turn):
            self.show_winner(myfont, turn)

        pygame.time.wait(5000)


    def draw_options_board(self):
        """Draw the option board: player x player and single player"""
        self.screen.fill(c.BACKGROUND_COLOR)
        font = pygame.font.Font("interface/fonts/FreckleFace-Regular.ttf", 150)        
        text_surface = font.render("Connect 4", True, c.TEXT_COLOR)
        text_rect = text_surface.get_rect()
        text_rect.center = (560, 230)
        self.screen.blit(text_surface, text_rect)
        self.draw_button(self.height/2 - 150, 350, 400, 70, "Player x Player")
        self.draw_button(self.height/2, 450, 400, 70, "Player x MCTS") 
        self.draw_button(self.height/2 - 90, 550, 400, 70, "A* x MCTS") 


    def choose_option(self) -> int:
        while True:
            game_mode = 0
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Redraw buttons with hover effects
            self.screen.fill(c.BACKGROUND_COLOR)
            font = pygame.font.Font("interface/fonts/FreckleFace-Regular.ttf", 150)        
            text_surface = font.render("Connect 4", True, c.TEXT_COLOR)
            text_rect = text_surface.get_rect(center=(560, 230))
            self.screen.blit(text_surface, text_rect)
            
            # Check hover for each button
            hover_player = (self.height/2 - 150 <= mouse_x <= self.height/2 - 150 + 400) and (350 <= mouse_y <= 350 + 70)
            hover_ai = (self.height/2 <= mouse_x <= self.height/2 + 400) and (450 <= mouse_y <= 450 + 70)
            hover_ai_vs_ai = (self.height/2 - 90 <= mouse_x <= self.height/2 - 90 + 400) and (550 <= mouse_y <= 550 + 70)
            
            # Draw buttons with hover state
            self.draw_button(self.height/2 - 150, 350, 400, 70, "Player x Player", hover_player)
            self.draw_button(self.height/2, 450, 400, 70, "Player x MCTS", hover_ai)
            self.draw_button(self.height/2 - 90, 550, 400, 70, "A* x MCTS", hover_ai_vs_ai)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    self.quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if hover_player:
                        print("Player vs Player selected")
                        game_mode = 1
                    elif hover_ai:
                        print("Player vs AI selected")
                        game_mode = 2
                    elif hover_ai_vs_ai:
                        print("AI vs AI selected")
                        game_mode = 3
            
            pygame.display.flip()
            
            if game_mode in [1, 2, 3]:
                return game_mode



    def draw_board(self) -> None:
        """Draw pygame board display"""
        self.screen.fill(c.BACKGROUND_COLOR)    

        # draw the board and its shadow:
        shadow_coordinates = (2*self.pixels-10, self.pixels-10, self.columns*self.pixels+24, self.rows*self.pixels+24)
        board_coordinates = (2*self.pixels-10, self.pixels-10, self.columns*self.pixels+20, self.rows*self.pixels+20)
        pygame.draw.rect(self.screen, c.SHADOW_COLOR, shadow_coordinates, 0, 30)  # draws the shadow with rounded corners
        pygame.draw.rect(self.screen, c.BOARD_COLOR, board_coordinates, 0, 30)  # draws the board with rounded corners

        # draw the board empty spaces:
        for col in range(self.columns):
            for row in range(self.rows):
                center_of_circle = (int((col+5/2)*self.pixels), int((row+3/2)*self.pixels))
                pygame.draw.circle(self.screen, c.BACKGROUND_COLOR, center_of_circle, self.rad)
        pygame.display.update()     

            
    def draw_new_piece(self, row: int, col: int, piece: int) -> None:
        center_of_circle = (int(col*self.pixels+self.pixels/2), self.height-int(row*self.pixels+self.pixels/2))
        pygame.draw.circle(self.screen, c.PIECES_COLORS[piece], center_of_circle, self.rad)


    def draw_button(self, x: int, y: int, width: int, height: int, text: str, hovered: bool = False) -> None:
        """Draw the option buttons with hover effect"""
        # Change color if hovered
        color = c.BUTTON_HOVER_COLOR if hovered else c.BUTTON_COLOR
        
        # Draw button (rounded corners with border_radius=30)
        pygame.draw.rect(self.screen, color, (x, y, width, height), 0, 30)
        
        # Draw text
        font = pygame.font.Font("interface/fonts/FreckleFace-Regular.ttf", 36)
        text_surface = font.render(text, True, c.TEXT_COLOR)
        text_rect = text_surface.get_rect(center=(x + width / 2, y + height / 2))
        self.screen.blit(text_surface, text_rect)


    def show_winner(self, myfont: any, turn: int) -> None:
        """Print the winner"""
        label = myfont.render("Player " + str(turn) +" wins!", turn, c.PIECES_COLORS[turn])
        self.screen.blit(label, (350,15))
        pygame.display.update()


    def show_draw(self, myfont: any) -> None:
        """Print draw game message"""
        label = myfont.render("Game tied!", True, c.BOARD_COLOR)
        self.screen.blit(label, (400,15))
        pygame.display.update()


    def quit() -> None:
        pygame.quit()
        sys.exit()

