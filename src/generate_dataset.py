import os
import numpy as np
import pandas as pd
import random
from game.board import Board
from game import constants as c
from game import rules as game
from ai.mcts import MCTS, Node

def generate_dataset(num_games=100, num_samples_per_game=1000):
    dataset = []
    os.makedirs('src/ai/datasets', exist_ok=True)  # Ensure directory exists

    for _ in range(num_games):
        board_obj = Board()
        board = board_obj.get_board()
        game_over = False
        current_player = c.PLAYER1_PIECE

        while not game_over:
            # Save state before move (with 20% probability)
            if random.random() < 0.2:
                flattened_board = [item for row in board for item in row]
                move_record = None  # Will be set after move is chosen
                outcome = None
                
                # Record the state before the move
                dataset.append(flattened_board + [None, None])  # Placeholder for move and outcome

            # Random move for Player 1
            if current_player == c.PLAYER1_PIECE:
                move = random.choice(game.available_moves(board))
            # MCTS move for Player 2 (fallback to random if MCTS fails)
            else:
                try:
                    root_node = Node(board=board, last_player=current_player)
                    mcts = MCTS(root_node)
                    move = mcts.search(3)
                except:
                    move = random.choice(game.available_moves(board))

            # Apply move
            board = game.simulate_move(board, current_player, move)

            # Check game end
            if game.winning_move(board, current_player):
                outcome = 'win' if current_player == c.PLAYER2_PIECE else 'loss'
                game_over = True
            elif game.is_game_tied(board):
                outcome = 'draw'
                game_over = True

            # Update the last recorded state with move and outcome if we saved this state
            if len(dataset) > 0 and dataset[-1][-1] is None:
                dataset[-1][-2] = move  # Update move
                dataset[-1][-1] = outcome if game_over else 'in_progress'

            # Switch player
            current_player = c.PLAYER2_PIECE if current_player == c.PLAYER1_PIECE else c.PLAYER1_PIECE

    # Filter out entries without moves (shouldn't happen with current logic)
    dataset = [sample for sample in dataset if sample[-2] is not None]
    
    # Save to CSV
    columns = [f'pos_{i}' for i in range(42)] + ['move', 'outcome']
    df = pd.DataFrame(dataset, columns=columns)
    df.to_csv('src/ai/datasets/connect4_dt.csv', index=False)
    return df

if __name__ == '__main__':
    print("Generating Connect Four dataset...")
    dataset = generate_dataset(num_games=100, num_samples_per_game=1000)
    print(f"Dataset generated with {len(dataset)} samples.")