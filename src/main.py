import pandas as pd
from mcts import MCTS, Node
from decision_tree import DecisionTree
from game_interface import play_game

def load_iris_dataset():
    # Carrega o dataset Iris
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
    columns = ["sepal_length", "sepal_width", "petal_length", "petal_width", "class"]
    data = pd.read_csv(url, names=columns)
    return data

def discretize_iris_data(data):
    # Discretiza os valores numéricos do dataset Iris
    for col in data.columns[:-1]:
        data[col] = pd.cut(data[col], bins=3, labels=["low", "medium", "high"])
    return data

def generate_connect_four_dataset():
    # Gera o dataset Connect Four usando o MCTS
    dataset = []
    for _ in range(1000):  # Gera 1000 estados de jogo
        mcts = MCTS([[0 for _ in range(7)] for _ in range(6)])
        mcts.search(100)  # Realiza 100 iterações do MCTS
        best_action = mcts.get_best_action()
        dataset.append((mcts.root.state, best_action))
    return pd.DataFrame(dataset, columns=["state", "move"])

def main():
    # 1. Carrega e discretiza o dataset Iris
    iris_data = load_iris_dataset()
    iris_data = discretize_iris_data(iris_data)
    print("Dataset Iris carregado e discretizado:")
    print(iris_data.head())

    # 2. Treina a árvore de decisão para o dataset Iris
    features = ["sepal_length", "sepal_width", "petal_length", "petal_width"]
    target = "class"
    dt = DecisionTree()
    dt.fit(iris_data, features, target)
    print("\nÁrvore de decisão treinada para o dataset Iris.")

    # 3. Gera o dataset Connect Four e treina a árvore de decisão
    connect_four_data = generate_connect_four_dataset()
    print("\nDataset Connect Four gerado:")
    print(connect_four_data.head())

    # 4. Executa o jogo Connect Four
    print("\nIniciando o jogo Connect Four...")
    play_game()

    # 5. Testa a árvore de decisão com novos dados (opcional)
    # Exemplo de previsão com a árvore de decisão
    sample = {"sepal_length": "low", "sepal_width": "medium", "petal_length": "high", "petal_width": "low"}
    prediction = dt.predict(sample)
    print(f"\nPrevisão para a amostra {sample}: {prediction}")

if __name__ == "__main__":
    main()