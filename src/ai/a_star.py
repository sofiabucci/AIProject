import numpy as np
from game import constants as c 
from game import rules as game
from ai import heuristic as h
import random

# Função que implementa o algoritmo A* simples para escolher o melhor movimento
def a_star(board: np.ndarray, ai_piece: int, opponent_piece: int) -> int:
    # Inicializa a melhor pontuação como negativo infinito
    move_score = float('-inf')
    # Inicializa a melhor jogada como inválida (-1)
    best_move = -1
    # Inicializa a melhor jogada do oponente para dica (opcional)
    best_opponent = 0
    # Lista todas as colunas válidas onde uma peça pode ser jogada
    possible_moves = game.available_moves(board)
    # Se só há uma jogada possível, retorna diretamente (evita lógica desnecessária)
    if len(possible_moves) == 1:
        return possible_moves[0]
    # Para cada jogada possível
    for col in possible_moves:
        # Simula a jogada do AI na coluna atual
        simulated_board = game.simulate_move(board, ai_piece, col)
        # Se essa jogada resulta em vitória imediata, retorna-a diretamente
        if game.winning_move(simulated_board, ai_piece): 
            return col
        # Simula a resposta do oponente usando a mesma função (papéis invertidos)
        opponent_col = a_star(simulated_board, opponent_piece, ai_piece)
        # Simula o tabuleiro após a jogada do oponente
        opponent_simulated_board = game.simulate_move(simulated_board, opponent_piece, opponent_col)
        # Avalia o tabuleiro após a jogada do AI e a resposta do oponente
        cur_score = h.calculate_board_score(opponent_simulated_board, ai_piece, opponent_piece)
        # Atualiza a melhor jogada se a pontuação atual for melhor
        if cur_score > move_score:
            best_opponent = opponent_col + 1  # Armazena a melhor resposta do oponente (+1 para mostrar como dica)
            best_move = col                   # Atualiza a melhor jogada do AI
            move_score = cur_score            # Atualiza a melhor pontuação
    # Exibe uma dica da resposta do oponente (opcional, para debug ou ajuda ao jogador)
    print("Dica de jogada: coluna " + str(best_opponent+1))
    # Retorna a melhor jogada encontrada
    return best_move
