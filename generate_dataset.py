# Importação de bibliotecas essenciais
import numpy as np
import pandas as pd
from game.board import Board                  # Classe para representar o tabuleiro
from game import constants as c               # Constantes como peças dos jogadores
from game import rules as game                # Regras do jogo (movimentos válidos, vitória, empate)
from ai.mcts import MCTS, Node                # IA com Monte Carlo Tree Search
import random

# Função para gerar um dataset simulando partidas de Connect Four
def generate_dataset(num_games=100, num_samples_per_game=1000):
    dataset = []  # Lista para armazenar os dados gerados

    for _ in range(num_games):  # Executa várias partidas
        board_obj = Board()                     # Inicializa novo tabuleiro
        board = board_obj.get_board()           # Obtém estado inicial do tabuleiro
        game_over = False                       # Flag de fim de jogo
        current_player = c.PLAYER1_PIECE        # Jogador 1 começa a partida

        while not game_over:
            if current_player == c.PLAYER1_PIECE:
                # Jogada aleatória para o Jogador 1
                available_moves = game.available_moves(board)
                move = random.choice(available_moves)
            else:
                # Jogada do Jogador 2 usando IA com MCTS
                root_node = Node(board=board, last_player=current_player)
                mcts = MCTS(root_node)
                move = mcts.search(3)  # Executa a busca por 3 segundos

            # 20% de chance de salvar este estado no dataset
            if random.random() < 0.2:
                # Converte o tabuleiro 2D em uma lista 1D
                flattened_board = [item for row in board for item in row]

                # Define o resultado da jogada se o jogo terminar aqui
                if game.winning_move(board, current_player):
                    outcome = 'win' if current_player == c.AI_PIECE else 'loss'
                elif game.is_game_tied(board):
                    outcome = 'draw'
                else:
                    outcome = None  # Não salva se o jogo ainda estiver em andamento

                if outcome:  # Só salva se houver resultado
                    dataset.append(flattened_board + [move, outcome])

            # Aplica a jogada no tabuleiro
            board = game.simulate_move(board, current_player, move)

            # Verifica fim de jogo
            if game.winning_move(board, current_player) or game.is_game_tied(board):
                game_over = True

            # Alterna o jogador
            current_player = (
                c.PLAYER2_PIECE if current_player == c.PLAYER1_PIECE else c.PLAYER1_PIECE
            )

    # Define os nomes das colunas (42 posições do tabuleiro + jogada + resultado)
    columns = [f'pos_{i}' for i in range(42)] + ['move', 'outcome']

    # Cria DataFrame com os dados
    df = pd.DataFrame(dataset, columns=columns)

    # Salva como CSV
    df.to_csv('datasets/connect4_dt.csv', index=False)

    return df

# Executa a geração do dataset se rodar o script diretamente
if __name__ == '__main__':
    print("Generating Connect Four dataset...")
    dataset = generate_dataset(num_games=100, num_samples_per_game=1000)
    print(f"Dataset generated with {len(dataset)} samples. Saved to datasets/connect4_dt.csv")
