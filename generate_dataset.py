import pandas as pd
import numpy as np
from game.board import Board
from ai.mcts import MCTSAgent
from ai.a_star import AStarAgent
import os
import csv
from datetime import datetime

def generate_training_data(num_games: int = 2000, filename: str = "data/connect4_training_data.csv") -> None:
    """Generate training data by simulating games between MCTS and A* agents"""
 
    
    with open(filename, 'w', newline='') as csvfile:
        # Feature names - adjust based on your actual feature vector size
        feature_names = [f"pos_{i}" for i in range(42)] + ["current_player"] + [f"pattern_{i}" for i in range(8)]
        header = feature_names + ["outcome"]
        writer = csv.writer(csvfile)
        writer.writerow(header)
        
        for game_num in range(1, num_games + 1):
            board = Board()
            mcts = MCTSAgent(iterations=1000)  # Reduced for faster testing
            astar = AStarAgent(max_depth=10)   # Reduced for faster testing
            
            move_count = 0
            max_moves = 42  # Maximum possible moves in Connect 4 (6x7)
            
            while not board.is_game_over and move_count < max_moves:
                move_count += 1
                
                try:
                    # Player 1 (MCTS)
                    move = mcts.get_best_move(board)
                    if not board.is_valid_move(move):
                        print(f"Invalid move {move} by MCTS in game {game_num}")
                        break
                    board.drop_piece(move)
                    
                    # Add training data from both perspectives
                    features_p1 = board.to_feature_vector(player_perspective=1)
                    features_p2 = board.to_feature_vector(player_perspective=2)
                    
                    # Determine outcome
                    if board.winner == 1:
                        result_p1, result_p2 = 1.0, 0.0
                    elif board.winner == 2:
                        result_p1, result_p2 = 0.0, 1.0
                    else:
                        result_p1 = result_p2 = 0.5
                    
                    writer.writerow(features_p1 + [result_p1])
                    writer.writerow(features_p2 + [result_p2])
                    
                    if board.is_game_over:
                        break
                        
                    # Player 2 (A*)
                    move = astar.get_best_move(board)
                    if not board.is_valid_move(move):
                        print(f"Invalid move {move} by A* in game {game_num}")
                        break
                    board.drop_piece(move)
                    
                    # Add training data from both perspectives
                    features_p1 = board.to_feature_vector(player_perspective=1)
                    features_p2 = board.to_feature_vector(player_perspective=2)
                    
                    # Determine outcome
                    if board.winner == 1:
                        result_p1, result_p2 = 1.0, 0.0
                    elif board.winner == 2:
                        result_p1, result_p2 = 0.0, 1.0
                    else:
                        result_p1 = result_p2 = 0.5
                    
                    writer.writerow(features_p1 + [result_p1])
                    writer.writerow(features_p2 + [result_p2])
                    
                except Exception as e:
                    print(f"Error in game {game_num}: {str(e)}")
                    break
            
            if game_num % 1 == 0:  # Print progress every game
                print(f"{datetime.now().strftime('%H:%M:%S')} - Completed game {game_num}/{num_games} (Moves: {move_count})")
                if board.winner:
                    print(f"Winner: Player {board.winner}")
                else:
                    print("Game ended in a draw")

if __name__ == "__main__":
    print("Starting data generation...")
    generate_training_data(num_games=2000)  # Start with fewer games for testing
    print("Data generation complete!")