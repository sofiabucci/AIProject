import pygame
import sys
from typing import Tuple, Optional
from game.board import Board

class GraphicalInterface:
    def __init__(self):
        # Cores modernas
        self.BACKGROUND = (18, 18, 29)  # Azul escuro quase preto
        self.BOARD_COLOR = (39, 42, 68)  # Azul escuro
        self.SLOT_COLOR = (24, 26, 44)  # Azul mais escuro
        self.PLAYER1_COLOR = (234, 67, 53)  # Vermelho vivo
        self.PLAYER2_COLOR = (251, 188, 5)  # Amarelo dourado
        self.TEXT_COLOR = (255, 255, 255)  # Branco
        self.ACCENT_COLOR = (88, 101, 242)  # Azul claro
        self.BUTTON_COLOR = (88, 101, 242)  # Azul claro
        self.BUTTON_HOVER = (71, 82, 196)  # Azul mais escuro
        
        # Configurações
        self.SQUARESIZE = 100
        self.RADIUS = int(self.SQUARESIZE/2 - 10)  # Menos espaço entre peças
        self.width = Board.COLS * self.SQUARESIZE
        self.height = (Board.ROWS + 1) * self.SQUARESIZE
        self.size = (self.width, self.height + 80)  # Espaço extra para informações
        
        # Inicialização
        pygame.init()
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption("Connect Four")
        self.title_font = pygame.font.SysFont("Arial", 50, bold=True)
        self.button_font = pygame.font.SysFont("Arial", 30)
        self.game_font = pygame.font.SysFont("Arial", 75)
        self.info_font = pygame.font.SysFont("Arial", 24)
        
        # Efeitos visuais
        self.animation_speed = 5

    def draw_menu(self):
        """Desenha o menu principal com opções de jogo"""
        self.screen.fill(self.BACKGROUND)
        
        # Título com efeito gradiente
        title = self.title_font.render("CONNECT FOUR", True, self.ACCENT_COLOR)
        shadow = self.title_font.render("CONNECT FOUR", True, (20, 20, 40))
        self.screen.blit(shadow, (self.width//2 - title.get_width()//2 + 3, 53))
        self.screen.blit(title, (self.width//2 - title.get_width()//2, 50))
        
        # Botões modernos
        buttons = [
            {"text": "Player vs Player", "rect": pygame.Rect(0, 0, 300, 60), "mode": 1},
            {"text": "Player vs Bot", "rect": pygame.Rect(0, 0, 300, 60), "mode": 2},
            {"text": "Bot vs Bot", "rect": pygame.Rect(0, 0, 300, 60), "mode": 3}
        ]
        
        for i, button in enumerate(buttons):
            button["rect"].center = (self.width//2, 220 + i*100)
            
            # Efeito hover
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = button["rect"].collidepoint(mouse_pos)
            
            # Desenha o botão com borda arredondada
            pygame.draw.rect(self.screen, 
                           self.BUTTON_HOVER if is_hovered else self.BUTTON_COLOR, 
                           button["rect"], 
                           border_radius=10)
            
            # Sombra do botão
            pygame.draw.rect(self.screen, (0, 0, 0, 50), 
                           (button["rect"].x, button["rect"].y + 5, 
                            button["rect"].width, button["rect"].height), 
                           border_radius=10)
            
            # Texto do botão
            text = self.button_font.render(button["text"], True, self.TEXT_COLOR)
            self.screen.blit(text, (button["rect"].centerx - text.get_width()//2, 
                            button["rect"].centery - text.get_height()//2))
        
        # Rodapé
        footer = self.info_font.render("© 2023 Connect Four", True, (100, 100, 120))
        self.screen.blit(footer, (self.width//2 - footer.get_width()//2, self.height - 30))
        
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

    def draw_board(self, board: Board):
        """Desenha o tabuleiro e as peças"""
        self.screen.fill(self.BACKGROUND)
        
        # Desenha o tabuleiro vazio com efeito 3D
        board_rect = pygame.Rect(0, self.SQUARESIZE, self.width, self.height - self.SQUARESIZE)
        pygame.draw.rect(self.screen, self.BOARD_COLOR, board_rect, border_radius=10)
        
        # Sombra do tabuleiro
        pygame.draw.rect(self.screen, (0, 0, 0, 100), 
                       (board_rect.x, board_rect.y + 5, 
                        board_rect.width, board_rect.height), 
                       border_radius=10)
        
        # Desenha os slots vazios
        for col in range(Board.COLS):
            for row in range(Board.ROWS):
                pygame.draw.circle(self.screen, self.SLOT_COLOR, 
                                 (int(col*self.SQUARESIZE + self.SQUARESIZE/2), 
                                  int((row+1.5)*self.SQUARESIZE)), 
                                  self.RADIUS + 2)
                pygame.draw.circle(self.screen, self.BOARD_COLOR, 
                                 (int(col*self.SQUARESIZE + self.SQUARESIZE/2), 
                                  int((row+1.5)*self.SQUARESIZE)), 
                                  self.RADIUS)
        
        # Desenha as peças com sombra
        for col in range(Board.COLS):
            for row in range(Board.ROWS):
                if board.state[row][col] == 1:
                    # Sombra
                    pygame.draw.circle(self.screen, (180, 50, 40), 
                                     (int(col*self.SQUARESIZE + self.SQUARESIZE/2) + 2, 
                                      int((row+1.5)*self.SQUARESIZE) + 2), 
                                      self.RADIUS)
                    # Peça
                    pygame.draw.circle(self.screen, self.PLAYER1_COLOR, 
                                     (int(col*self.SQUARESIZE + self.SQUARESIZE/2), 
                                      int((row+1.5)*self.SQUARESIZE)), 
                                      self.RADIUS)
                elif board.state[row][col] == 2:
                    # Sombra
                    pygame.draw.circle(self.screen, (200, 160, 0), 
                                     (int(col*self.SQUARESIZE + self.SQUARESIZE/2) + 2, 
                                      int((row+1.5)*self.SQUARESIZE) + 2), 
                                      self.RADIUS)
                    # Peça
                    pygame.draw.circle(self.screen, self.PLAYER2_COLOR, 
                                     (int(col*self.SQUARESIZE + self.SQUARESIZE/2), 
                                      int((row+1.5)*self.SQUARESIZE)), 
                                      self.RADIUS)
        
        # Barra de informações superior
        info_rect = pygame.Rect(0, 0, self.width, self.SQUARESIZE)
        pygame.draw.rect(self.screen, (30, 32, 50), info_rect)
        
        # Mostra de quem é a vez
        turn_text = self.button_font.render(
            f"Vez do Jogador {board.current_player}", 
            True, 
            self.PLAYER1_COLOR if board.current_player == 1 else self.PLAYER2_COLOR
        )
        self.screen.blit(turn_text, (20, 20))
        
        # Mostra os jogadores
        player1_text = self.info_font.render("Jogador 1", True, self.PLAYER1_COLOR)
        player2_text = self.info_font.render("Jogador 2", True, self.PLAYER2_COLOR)
        self.screen.blit(player1_text, (self.width - 200, 20))
        self.screen.blit(player2_text, (self.width - 200, 50))
        
        # Ícones dos jogadores
        pygame.draw.circle(self.screen, self.PLAYER1_COLOR, (self.width - 250, 30), 10)
        pygame.draw.circle(self.screen, self.PLAYER2_COLOR, (self.width - 250, 60), 10)
        
        pygame.display.update()

    def animate_piece_drop(self, board: Board, col: int, row: int):
        """Anima a queda de uma peça"""
        x_pos = col * self.SQUARESIZE + self.SQUARESIZE // 2
        color = self.PLAYER1_COLOR if board.current_player == 1 else self.PLAYER2_COLOR
        shadow_color = (180, 50, 40) if board.current_player == 1 else (200, 160, 0)
        
        for y in range(0, (row + 1) * self.SQUARESIZE + self.SQUARESIZE // 2, self.animation_speed):
            # Redesenha o tabuleiro sem a peça que está caindo
            self.draw_board(board)
            
            # Desenha a peça caindo
            pygame.draw.circle(self.screen, shadow_color, (x_pos + 2, y + 2), self.RADIUS)
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