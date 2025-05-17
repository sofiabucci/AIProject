import numpy as np
from game import constants as c 
from game import rules as game
from ai import heuristic as h
import random

# Função que implementa o algoritmo A* simples para escolher o melhor movimento
def a_star(board: np.ndarray, ai_piece: int, opponent_piece: int) -> int:
    best_score = float('-inf')  # Inicializa a melhor pontuação como negativo infinito
    best_move = -1  # Inicializa o melhor movimento como inválido

    # Itera por todos os movimentos disponíveis no tabuleiro
    for col in game.available_moves(board):
        # Simula o tabuleiro após fazer o movimento na coluna `col`
        simulated_board = game.simulate_move(board, ai_piece, col)
        
        # Calcula a pontuação heurística do tabuleiro simulado
        cur_score = h.calculate_board_score(simulated_board, ai_piece, opponent_piece)
        
        # Se a pontuação for melhor do que a melhor encontrada até agora, atualiza
        if cur_score > best_score:
            best_move = col
            best_score = cur_score

    # Retorna a coluna com a melhor pontuação
    return best_move


