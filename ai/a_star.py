import numpy as np
from game import constants as c 
from game import rules as game
from ai import heuristic as h
import random


def a_star(board: np.ndarray, ai_piece: int, opponent_piece: int) -> int:
    best_score = float('-inf')
    best_move = -1
    for col in game.available_moves(board):
        simulated_board = game.simulate_move(board, ai_piece, col)
        cur_score = h.calculate_board_score(simulated_board, ai_piece, opponent_piece)
        if cur_score > best_score:
            best_move = col
            best_score = cur_score
    return best_move


# In a_star.py, modify the a_star_adversarial function:
def a_star_adversarial(board: np.ndarray, ai_piece: int, opponent_piece: int) -> int:
    move_score = float('-inf')
    best_move = -1
    possible_moves = game.available_moves(board)
    
    if len(possible_moves) == 1:
        return possible_moves[0]

    for col in possible_moves:
        simulated_board = game.simulate_move(board, ai_piece, col)
        
        # If this move wins immediately, take it
        if game.winning_move(simulated_board, ai_piece):
            return col
            
        # Evaluate opponent's best response
        opponent_best_score = float('-inf')
        opponent_best_move = -1
        for opp_col in game.available_moves(simulated_board):
            opp_simulated = game.simulate_move(simulated_board, opponent_piece, opp_col)
            score = h.calculate_board_score(opp_simulated, ai_piece, opponent_piece)
            if score > opponent_best_score:
                opponent_best_score = score
                opponent_best_move = opp_col
        
        if opponent_best_move != -1:
            final_board = game.simulate_move(simulated_board, opponent_piece, opponent_best_move)
            cur_score = h.calculate_board_score(final_board, ai_piece, opponent_piece)
            
            if cur_score > move_score:
                best_move = col
                move_score = cur_score

    return best_move if best_move != -1 else random.choice(possible_moves)





