import pandas as pd
from ai.mcts import MCTS

def load_iris_dataset():
    """Carrega o dataset Iris"""
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
    columns = ["sepal_length", "sepal_width", "petal_length", "petal_width", "class"]
    return pd.read_csv(url, names=columns)

def discretize_iris_data(data):
    """Discretiza os valores numéricos do dataset Iris"""
    for col in data.columns[:-1]:
        data[col] = pd.cut(data[col], bins=3, labels=["low", "medium", "high"])
    return data

def generate_connect_four_dataset(samples: int = 1000):
    """Gera o dataset Connect Four usando o MCTS"""
    from game.board import Board
    
    dataset = []
    for _ in range(samples):
        board = Board()
        mcts = MCTS(board, iterations=100)
        best_move = mcts.search()
        dataset.append({
            "state": board.state,
            "move": best_move,
            "player": board.get_current_player()
        })
    
    return pd.DataFrame(dataset)