import numpy as np
import pandas as pd
from game.board import Board
from game import constants as c
from game import rules as game
from ai.mcts import MCTS, Node  
import random

def generate_dataset(num_games=100, num_samples_per_game=1000):
    dataset = []
    
    for _ in range(num_games):
        board_obj = Board()
        board = board_obj.get_board()
        game_over = False
        current_player = c.PLAYER1_PIECE
        
        while not game_over:
            if current_player == c.PLAYER1_PIECE:
                # Random move for Player 1
                available_moves = game.available_moves(board)
                move = random.choice(available_moves)
            else:
                # AI move (MCTS) for Player 2
                root_node = Node(board=board, last_player=current_player)
                mcts = MCTS(root_node)
                move = mcts.search(3)  # Search for best move (3 seconds max)
            
            # Record the state and move (20% sampling)
            if random.random() < 0.2:
                flattened_board = [item for sublist in board for item in sublist]
                # Determine game outcome (simplified for example)
                if game.winning_move(board, current_player):
                    outcome = 'win' if current_player == c.AI_PIECE else 'loss'
                elif game.is_game_tied(board):
                    outcome = 'draw'
                else:
                    outcome = None  # Skip if game isn't over yet
                
                if outcome:  # Only save if the move leads to a conclusion
                    dataset.append(flattened_board + [move, outcome])
            
            # Simulate the move
            board = game.simulate_move(board, current_player, move)
            
            # Check for game over
            if game.winning_move(board, current_player) or game.is_game_tied(board):
                game_over = True
            
            # Switch player
            current_player = c.PLAYER2_PIECE if current_player == c.PLAYER1_PIECE else c.PLAYER1_PIECE
    
    # Save to CSV with column names
    columns = [f'pos_{i}' for i in range(42)] + ['move', 'outcome']
    df = pd.DataFrame(dataset, columns=columns)
    df.to_csv('datasets/connect4_dt.csv', index=False)
    return df

if __name__ == '__main__':
    print("Generating Connect Four dataset...")
    dataset = generate_dataset(num_games=100, num_samples_per_game=1000)
    print(f"Dataset generated with {len(dataset)} samples. Saved to datasets/connect4_dt.csv")