def print_board(board):
    for row in board:
        print("|".join(str(cell) for cell in row))
        print("-" * 13)

def play_game():
    board = [[0 for _ in range(7)] for _ in range(6)]
    current_player = 1
    while True:
        print_board(board)
        if current_player == 1:
            col = int(input("Jogador 1, escolha uma coluna (0-6): "))
        else:
            mcts = MCTS(board)
            mcts.search(1000)  # Número de iterações
            col = mcts.get_best_action()
        # Implemente a lógica para atualizar o tabuleiro e verificar vitória