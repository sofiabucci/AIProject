import pandas as pd
from sklearn.model_selection import train_test_split
from ai.decision_tree import DecisionTree
from ai.mcts import MCTS
from interface.cli import CLIGame, HumanPlayer, AIPlayer
from data.datasets import load_iris_dataset, discretize_iris_data, generate_connect_four_dataset

def main():
    # 1. Carrega e discretiza o dataset Iris
    iris_data = load_iris_dataset()
    iris_data = discretize_iris_data(iris_data)
    print("Dataset Iris carregado e discretizado:")
    print(iris_data.head())

    # 2. Treina a árvore de decisão para o dataset Iris
    features = ["sepal_length", "sepal_width", "petal_length", "petal_width"]
    target = "class"
    X = iris_data[features]
    y = iris_data[target]
    
    dt = DecisionTree(max_depth=3)
    dt.fit(X, y)
    print("\nÁrvore de decisão treinada para o dataset Iris.")

    # 3. Gera o dataset Connect Four
    connect_four_data = generate_connect_four_dataset()
    print("\nDataset Connect Four gerado:")
    print(connect_four_data.head())

    # 4. Executa o jogo Connect Four
    print("\n=== Iniciando Jogo Connect4 ===")
    print("Modos disponíveis:")
    print("1. Humano vs IA")
    print("2. IA vs IA")
    print("3. Humano vs Humano")
    
    choice = input("Escolha um modo (1-3): ")
    
    if choice == '1':
        player1 = HumanPlayer()
        player2 = AIPlayer(iterations=1000)
    elif choice == '2':
        player1 = AIPlayer(iterations=1000)
        player2 = AIPlayer(iterations=1000)
    elif choice == '3':
        player1 = HumanPlayer()
        player2 = HumanPlayer()
    else:
        print("Opção inválida. Usando Humano vs IA como padrão.")
        player1 = HumanPlayer()
        player2 = AIPlayer(iterations=1000)
    
    game = CLIGame(player1, player2)
    game.play()

    # 5. Testa a árvore de decisão com novos dados
    sample = {"sepal_length": "low", "sepal_width": "medium", 
              "petal_length": "high", "petal_width": "low"}
    prediction = dt.predict(sample)
    print(f"\nPrevisão para a amostra {sample}: {prediction}")

if __name__ == "__main__":
    main()