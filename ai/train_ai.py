import pandas as pd
import numpy as np
from game.board import Board
from mcts import MCTSAgent
from a_star import AStar
from decision_tree import DecisionTree
import random

def generate_training_data(num_games: int = 1000) -> pd.DataFrame:
    data = []
    
    for _ in range(num_games):
        board = Board()
        mcts = MCTSAgent(iterations=1000)
        astar = AStar(board, 2)
        
        while not board.is_game_over:
            # Jogador 1 (MCTS)
            move = mcts.get_best_move(board)
            board.drop_piece(move)
            if board.is_game_over:
                break
                
            # Jogador 2 (A*)
            move = astar.search()
            board.drop_piece(move)
            
            # Adiciona dados de treinamento
            features = board.to_feature_vector()
            result = 0.5  # empate por padrão
            if board.winner == 1:
                result = 1.0
            elif board.winner == 2:
                result = 0.0
            data.append(features + [result])
    
    columns = [f"f{i}" for i in range(len(data[0])-1)] + ["result"]
    return pd.DataFrame(data, columns=columns)

def train_decision_tree(data: pd.DataFrame) -> DecisionTree:
    X = data.iloc[:, :-1]
    y = data.iloc[:, -1]
    
    dt = DecisionTree(max_depth=10, min_samples_split=5)
    dt.fit(X, y)
    
    # Avaliação simples
    train_score = dt.score(X, y)
    print(f"Decision Tree trained with score: {train_score:.2f}")
    
    return dt

if __name__ == "__main__":
    print("Generating training data...")
    training_data = generate_training_data(500)
    training_data.to_csv("connect4_training_data.csv", index=False)
    
    print("Training Decision Tree...")
    dt = train_decision_tree(training_data)
    
    # Salvar o modelo treinado (implementar se necessário)
    print("Training complete!")