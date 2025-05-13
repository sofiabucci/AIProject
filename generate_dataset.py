import csv
import random
from ai.mcts import MCTSAgent
from game.board import Board

def generate_data(num_games: int = 2000, filename: str = 'data/connect4_data.csv'):
    agent = MCTSAgent(iterations=500)
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([f'pos_{i}' for i in range(42)] + ['move'])
        
        for game in range(num_games):
            board = Board()
            while not board.is_game_over:
                try:
                    if board.current_player == 1:
                        move = random.choice(board.get_legal_moves())
                    else:
                        move = agent.get_best_move(board)
                    
                    # Verificação adicional de segurança
                    if not board.is_valid_move(move):
                        print(f"Invalid move {move} generated, skipping game")
                        break
                    
                    features = board.to_feature_vector()
                    writer.writerow(features + [move])
                    board.drop_piece(move)
                
                except Exception as e:
                    print(f"Error in game {game}: {str(e)}")
                    break
            
            if (game + 1) % 100 == 0:
                print(f"Generated {game + 1}/{num_games} games")

if __name__ == "__main__":
    generate_data()