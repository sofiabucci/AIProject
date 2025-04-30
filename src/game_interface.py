from mcts import MCTS
import game as gm

COLS = 7
ROWS = 6

def print_board(board):
    for row in board:
        print("|".join(str(cell) for cell in row))
        print("-" * 13)

def play_game():
    mode = int(input("Escolher modo de jogo: \n" \
    "1. Jogador vs. Jogador\n" \
    "2. Jogador vs. Bot\n" \
    "3. Bot vs. Bot"))
    match mode:
        case 1: play_against_player()
        case 2: play_against_ai()
        case 3: ai_against_ai()
        case _: exit(ValueError)


def play_against_player():
    board = [[0 for _ in range(7)] for _ in range(6)]
    current_player = 1
    while True:   
        print_board(board)
        if current_player == 1:
            col = int(input("Jogador 1, escolha uma coluna (0-6): "))
            row = find_row(board, col,current_player)
            board[col][row] = current_player
            #checar se venceu se nao atualizar o jogador
            if next_player(won_game(board, current_player, col, row)) == 0:
                current_player = 2
        else:
            col = int(input("Jogador 2, escolha uma coluna (0-6): "))
            row = find_row(board, col, current_player)
            # atualizar tabuleiro
            board[col][row] = current_player
            #checar se venceu se nao atualizar o jogador
            if next_player(won_game(board, current_player, col, row)) == 0:
                current_player = 1

def play_against_ai():
    board = [[0 for _ in range(7)] for _ in range(6)]
    current_player = 1
    while True:
        print_board(board)
        if current_player == 1:
            col = int(input("Jogador 1, escolha uma coluna (0-6): "))
            row = find_row(board, col, current_player)
            # atualizar tabuleiro
            board[col][row] = current_player
            #checar se venceu se nao atualizar o jogador
            if next_player(won_game(board, current_player, col, row)) == 0:
                current_player = 2
        else:
            print("Bot escolhendo jogada...")
            mcts = MCTS(board)
            mcts.search(1000)  # Número de iterações
            col = mcts.get_best_action()
            row = find_row(board, col, current_player)
            # atualizar tabuleiro
            board[col][row] = current_player
            #checar se venceu se nao atualizar o jogador
            if next_player(won_game(board, current_player, col, row)) == 0:
                current_player = 1
        # Implemente a lógica para atualizar o tabuleiro e verificar vitória

def ai_against_ai():
    board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    current_player = 1
    while True:
        print_board(board)
        if current_player == 1:
            # outro algoritimo ai
            row = find_row(board, col, current_player)
            # atualizar tabuleiro
            board[col][row] = current_player
            # checar se venceu se nao atualizar o jogador
            if next_player(won_game(board, current_player, col, row)) == 0:
                current_player = 2
        else:
            print("Bot 2 escolhendo jogada... ")
            mcts = MCTS(board)
            mcts.search(1000)  # Número de iterações
            col = mcts.get_best_action()
            row = find_row(board, col, current_player)
            board[col][row] = current_player
            #checar se venceu se nao atualizar o jogador
            if next_player(won_game(board, current_player, col, row)) == 0:
                current_player = 1
        # Implemente a lógica para atualizar o tabuleiro e verificar vitória

def next_player(i):
    match i:
        case 1:
            print("Jogador 1 ganhou!!")
            exit()
        case 2:
            print("Jogador 2 ganhou!!")
            exit()
        case 0:
            return 0
        case -1:
            print("Empate!!")
            exit()
        case _:
            exit(ValueError)


def won_game(board, player, col, row):
    # checar horizontais
    count = 1
    i = col + 1
    while i < COLS and board[row][i] ==player : 
        count, i = count + 1, i + 1
    i = col - 1
    while i >= 0 and board[row][i] == player : 
        count, i = count + 1, i-1
    if count >= 4: 
        return player
    
    # checar vertical
    if row >= 3 and board[row - 1][col] == player and board[row - 2][col] == player and board[row - 3][col] == player:
        return player

    # checar diagonais
    count = 1
    i = 1
    while row+i < ROWS and col+i < COLS and board[row+i][col+i] == player: 
        count, i = count+1, i+1
    i = - 1
    while row+i >= 0 and col+i >= 0 and board[row+i][col+i] == player: 
        count, i = count+1, i-1
    if count >= 4: 
        return player
    
    count = 1
    i = 1
    while row+i < ROWS and col-i >= 0 and board[row+i][col+i] == player: 
        count, i = count+1, i+1
    i = - 1
    while row+i >= 0 and col-i < COLS and board[row+i][col+i] == player: 
        count, i = count+1, i-1
    if count >= 4: 
        return player
    # checar empate
    for i in range(COLS):
        if board[ROWS-1][COLS] == 0:
            return 0
    return -1

def find_row(board, col):
    i = 0
    for pos in board[col]:
        if not pos == 1: i+1
    return i

