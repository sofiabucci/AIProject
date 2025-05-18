import pygame 
import itertools
import sys
from game import constants as c
from game.board import Board
import game.rules as game
from dataclasses import dataclass


@dataclass
class Interface:
    # Parâmetros padrão definidos a partir de constantes
    rows: int = c.ROWS
    columns: int = c.COLUMNS
    pixels: int = c.SQUARESIZE
    width: int = c.WIDTH
    height: int = c.HEIGHT
    rad: float = c.RADIUS
    size: tuple = (width, height)
    screen: any = pygame.display.set_mode(size)  # Janela do pygame

    pygame.display.set_caption("Connect4")  # Título da janela


    def start_game(self, bd: Board) -> None:
        """Inicializa o jogo, mostra as opções e começa a execução"""
        pygame.init()
        self.draw_options_board()  # Desenha o menu inicial
        game_mode = self.choose_option()  # Usuário escolhe modo de jogo
        bd.print_board()	
        self.draw_board()    # Desenha o tabuleiro vazio
        pygame.display.update()
        self.play_game(bd, game_mode)  # Começa a partida


    def play_game(self, bd: Board, game_mode: int) -> None:
        """Executa o loop principal do jogo"""
        board = bd.get_board()	
        game_over = False
        myfont = pygame.font.SysFont("Monospace", 50, bold=True)
        turns = itertools.cycle([1, 2])  # Alternância de turnos
        turn = next(turns)
        
        while not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    self.quit()

                # Movimento humano (somente nos modos 1 e 2)
                if game_mode != 3:
                    if event.type == pygame.MOUSEMOTION:
                        pygame.draw.rect(self.screen, c.BACKGROUND_COLOR, (0, 0, self.width, self.pixels - 14))
                        posx = event.pos[0]
                        pygame.draw.circle(self.screen, c.PIECES_COLORS[turn], (posx, int(self.pixels / 2) - 7), self.rad)
                        pygame.display.update()

                    if event.type == pygame.MOUSEBUTTONDOWN and (turn == 1 or (turn == 2 and game_mode == 1)):
                        if not game.human_move(bd, self, board, turn, event): 
                            continue
                        if game.winning_move(board, turn): 
                            game_over = True
                            break
                        turn = next(turns)

            # Movimento de IA (modo 2 ou 3)
            if (game_mode == 2 and turn == 2) or game_mode == 3:
                pygame.time.wait(500)  # Espera para visualizar jogada
                game_over = game.ai_move(bd, self, game_mode, board, turn)
                if game_over: 
                    break
                turn = next(turns)

            if game.is_game_tied(board):
                self.show_draw(myfont)
                break

        if game.winning_move(board, turn):
            self.show_winner(myfont, turn)

        pygame.time.wait(5000)  # Espera antes de fechar


    def draw_options_board(self):
        """Desenha a tela inicial com os modos de jogo"""
        self.screen.fill(c.BACKGROUND_COLOR)
        font = pygame.font.Font("src/interface/fonts/FreckleFace-Regular.ttf", 150)        
        text_surface = font.render("Connect 4", True, c.TEXT_COLOR)
        text_rect = text_surface.get_rect(center=(560, 230))
        self.screen.blit(text_surface, text_rect)
        self.draw_button(self.height / 2 - 150, 350, 400, 70, "Player x Player")
        self.draw_button(self.height / 2, 450, 400, 70, "Player x MCTS") 
        self.draw_button(self.height / 2 - 90, 550, 400, 70, "Decision Tree x MCTS") 


    def choose_option(self) -> int:
        """Permite ao jogador escolher o modo de jogo clicando nos botões"""
        while True:
            game_mode = 0
            mouse_x, mouse_y = pygame.mouse.get_pos()

            self.screen.fill(c.BACKGROUND_COLOR)
            font = pygame.font.Font("src/interface/fonts/FreckleFace-Regular.ttf", 150)        
            text_surface = font.render("Connect 4", True, c.TEXT_COLOR)
            text_rect = text_surface.get_rect(center=(560, 230))
            self.screen.blit(text_surface, text_rect)

            # Detecta hover sobre os botões
            hover_player = (self.height / 2 - 150 <= mouse_x <= self.height / 2 - 150 + 400) and (350 <= mouse_y <= 350 + 70)
            hover_ai = (self.height / 2 <= mouse_x <= self.height / 2 + 400) and (450 <= mouse_y <= 450 + 70)
            hover_ai_vs_ai = (self.height / 2 - 90 <= mouse_x <= self.height / 2 - 90 + 400) and (550 <= mouse_y <= 550 + 70)

            # Redesenha botões com efeito de hover
            self.draw_button(self.height / 2 - 150, 350, 400, 70, "Player x Player", hover_player)
            self.draw_button(self.height / 2, 450, 400, 70, "Player x MCTS", hover_ai)
            self.draw_button(self.height / 2 - 90, 550, 400, 70, "Decision Tree x MCTS", hover_ai_vs_ai)

            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    self.quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if hover_player:
                        print("Player vs Player selecionado")
                        game_mode = 1
                    elif hover_ai:
                        print("Player vs AI selecionado")
                        game_mode = 2
                    elif hover_ai_vs_ai:
                        print("AI vs AI selecionado")
                        game_mode = 3
            
            pygame.display.flip()

            if game_mode in [1, 2, 3]:
                return game_mode


    def draw_board(self) -> None:
        """Desenha o tabuleiro principal do jogo"""
        self.screen.fill(c.BACKGROUND_COLOR)    

        # Desenha tabuleiro com sombra
        shadow_coordinates = (2*self.pixels - 10, self.pixels - 10, self.columns*self.pixels + 24, self.rows*self.pixels + 24)
        board_coordinates = (2*self.pixels - 10, self.pixels - 10, self.columns*self.pixels + 20, self.rows*self.pixels + 20)
        pygame.draw.rect(self.screen, c.SHADOW_COLOR, shadow_coordinates, 0, 30)
        pygame.draw.rect(self.screen, c.BOARD_COLOR, board_coordinates, 0, 30)

        # Desenha círculos (vazios) no tabuleiro
        for col in range(self.columns):
            for row in range(self.rows):
                center = (int((col + 5 / 2) * self.pixels), int((row + 3 / 2) * self.pixels))
                pygame.draw.circle(self.screen, c.BACKGROUND_COLOR, center, self.rad)
        pygame.display.update()


    def draw_new_piece(self, row: int, col: int, piece: int) -> None:
        """Desenha uma nova peça no tabuleiro"""
        center = (int(col * self.pixels + self.pixels / 2), self.height - int(row * self.pixels + self.pixels / 2))
        pygame.draw.circle(self.screen, c.PIECES_COLORS[piece], center, self.rad)


    def draw_button(self, x: int, y: int, width: int, height: int, text: str, hovered: bool = False) -> None:
        """Desenha um botão interativo com texto"""
        color = c.BUTTON_HOVER_COLOR if hovered else c.BUTTON_COLOR
        pygame.draw.rect(self.screen, color, (x, y, width, height), 0, 30)
        font = pygame.font.Font("src/interface/fonts/FreckleFace-Regular.ttf", 36)
        text_surface = font.render(text, True, c.TEXT_COLOR)
        text_rect = text_surface.get_rect(center=(x + width / 2, y + height / 2))
        self.screen.blit(text_surface, text_rect)


    def show_winner(self, myfont: any, turn: int) -> None:
        """Exibe mensagem de vitória"""
        label = myfont.render("Player " + str(turn) + " wins!", True, c.PIECES_COLORS[turn])
        self.screen.blit(label, (350, 15))
        pygame.display.update()


    def show_draw(self, myfont: any) -> None:
        """Exibe mensagem de empate"""
        label = myfont.render("Game tied!", True, c.BOARD_COLOR)
        self.screen.blit(label, (400, 15))
        pygame.display.update()


    def quit() -> None:
        """Encerra o jogo"""
        pygame.quit()
        sys.exit()
