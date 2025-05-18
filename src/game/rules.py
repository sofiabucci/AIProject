# Importação de bibliotecas e módulos necessários
import game.constants as c  # Constantes do jogo, como dimensões, cores e peças
import numpy as np  # Biblioteca para manipulação de arrays (tabuleiro)
import math  # Biblioteca para funções matemáticas
import pygame  # Biblioteca para interface gráfica
from game.board import Board  # Classe que representa o tabuleiro
from ai import a_star as g, decision_tree as tree, mcts as m  # Importação dos algoritmos de IA

# Função responsável pela jogada do jogador humano
def human_move(bd: Board, interface: any, board: np.ndarray, turn: int, event: any) -> bool:
    """Define a coluna onde o jogador humano jogou"""
    col = get_human_column(interface, event)  # Obtém a coluna a partir do clique do mouse
    if not is_valid(board, col): 
        return False  # Movimento inválido se a coluna estiver cheia ou fora do tabuleiro

    # Atualiza a interface apagando a linha superior
    pygame.draw.rect(interface.screen, c.BACKGROUND_COLOR, (0,0, interface.width, interface.pixels-14))   
    make_move(bd, interface, board, turn, col)  # Realiza o movimento
    return True  # Movimento válido

# Função que obtém a coluna clicada pelo jogador com base na posição do mouse
def get_human_column(interface: any, event: any):
    posx = event.pos[0]  # Posição X do mouse
    col = int(math.floor(posx / interface.pixels)) - 2  # Traduz coordenada para coluna
    return col

# Retorna uma lista com todas as colunas que ainda aceitam peças
def available_moves(board: np.ndarray) -> list | int:
    avaiable_moves = []
    for i in range(c.COLUMNS):
        if board[5][i] == 0:  # Verifica a linha do topo
            avaiable_moves.append(i)
    return avaiable_moves if len(avaiable_moves) > 0 else -1

# Função principal que comanda a jogada da IA
def ai_move(bd: Board, interface: any, game_mode: int, board: np.ndarray, turn: int) -> int:
    """Define a coluna onde a IA vai jogar"""
    ai_column = get_ai_column(board, game_mode)  # Escolhe a jogada com base no algoritmo
    game_over = make_move(bd, interface, board, turn, ai_column)  # Realiza a jogada
    return game_over  # Retorna se o jogo terminou

# Função que decide qual algoritmo de IA será usado de acordo com o modo de jogo
def get_ai_column(board: np.ndarray, game_mode: int) -> int:
    if game_mode == 2:  
        return m.mcts(board)  # Modo 2 usa Monte Carlo Tree Search
    elif game_mode == 3:  
        # Alternância entre MCTS e A* baseado no número de peças
        x_count = np.count_nonzero(board == 1)
        o_count = np.count_nonzero(board == 2)
        if x_count == o_count:  # Vez do X (MCTS)
            return m.mcts(board)
        else:  # Vez do O (A*)
            return g.a_star(board, c.PLAYER1_PIECE, c.PLAYER2_PIECE)

# Simula um movimento sem alterar o tabuleiro real
def simulate_move(board: np.ndarray, piece: int, col: int) -> np.ndarray:
    board_copy = board.copy()
    row = get_next_open_row(board_copy, col)
    drop_piece(board_copy, row, col, piece)
    return board_copy

# Executa o movimento no tabuleiro e desenha na tela
def make_move(bd: Board, interface: any, board: np.ndarray, turn: int, move: int):
    row = get_next_open_row(board, move)  # Encontra a linha disponível
    drop_piece(board, row, move, turn)  # Atualiza o tabuleiro
    interface.draw_new_piece(row+1, move+2, turn)  # Desenha na interface
    pygame.display.update()  # Atualiza a tela
    bd.print_board()  # Imprime o tabuleiro no terminal (debug)

    # Verifica se o jogo terminou com vitória ou empate
    return winning_move(board, turn) or is_game_tied(board)

# Retorna a primeira linha disponível em uma coluna
def get_next_open_row(board: np.ndarray, col: int) -> int:
    for row in range(c.ROWS):
        if board[row][col] == 0:
            return row
    return -1  # Nenhuma linha disponível

# Insere a peça no tabuleiro
def drop_piece(board: np.ndarray, row: int, col: int, piece: int) -> None:
    board[row][col] = piece

# Verifica se o jogo empatou (tabuleiro cheio sem vencedores)
def is_game_tied(board: np.ndarray) -> bool:
    if winning_move(board, c.PLAYER1_PIECE) or winning_move(board, c.PLAYER2_PIECE): 
        return False
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 0: 
                return False  # Ainda há jogadas possíveis
    return True  # Tabuleiro cheio e sem vencedor

# Verifica se a coluna selecionada é válida
def is_valid(board: np.ndarray, col: int) -> bool:
    if not 0 <= col < c.COLUMNS: 
        return False  # Fora do intervalo de colunas
    row = get_next_open_row(board, col)
    return 0 <= row <= 5  # Há uma linha disponível

# Verifica se o movimento atual resulta em vitória
def winning_move(board: np.ndarray, piece: int) -> bool:
    """Verifica todas as direções possíveis de vitória"""
    
    # Horizontal
    def check_horizontal(board: np.ndarray, piece: int) -> bool:
        for col in range(c.COLUMNS - 3):
            for row in range(c.ROWS):
                if all(board[row][col+i] == piece for i in range(4)):
                    return True

    # Vertical
    def check_vertical(board: np.ndarray, piece: int) -> bool:
        for col in range(c.COLUMNS):
            for row in range(c.ROWS - 3):
                if all(board[row+i][col] == piece for i in range(4)):
                    return True

    # Diagonal crescente
    def check_ascending_diagonal(board: np.ndarray, piece: int) -> bool:
        for col in range(c.COLUMNS - 3):
            for row in range(c.ROWS - 3):
                if all(board[row+i][col+i] == piece for i in range(4)):
                    return True

    # Diagonal decrescente
    def check_descending_diagonal(board: np.ndarray, piece: int) -> bool:
        for col in range(c.COLUMNS - 3):
            for row in range(3, c.ROWS):
                if all(board[row-i][col+i] == piece for i in range(4)):
                    return True

    # Retorna verdadeiro se qualquer direção gerar vitória
    return (
        check_vertical(board, piece) or 
        check_horizontal(board, piece) or 
        check_ascending_diagonal(board, piece) or 
        check_descending_diagonal(board, piece)
    )
