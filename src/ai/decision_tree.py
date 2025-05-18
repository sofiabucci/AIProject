# Importações necessárias
from typing import Union
import numpy as np
import os
import pandas as pd
import random
from pandas import DataFrame, Series, read_csv
from game import rules as game        # Importa regras do jogo Connect4
from game import constants as c       
from joblib import load, dump         # Para salvar e carregar modelos com persistência

# Classe que representa um nó da árvore de decisão
class DTNode:
    def __init__(self, feature_index=None, feature_name=None, children=None, info_gain=None, split_values=None, leaf_value=None) -> None:
        self.feature_index = feature_index      # Índice do atributo usado para o split
        self.feature_name = feature_name        # Nome do atributo
        self.children = children                # Dicionário de nós filhos
        self.info_gain = info_gain              # Ganho de informação do split
        self.split_values = split_values        # Valores do atributo para cada ramo
        self.leaf_value = leaf_value            # Valor da classe se o nó for uma folha

# Classe que constrói e faz previsões com árvore de decisão
class DecisionTreeClassifier:
    def __init__(self, max_depth: int = None, min_samples_split: int = None, criterium: str = 'entropy') -> None:
        self.root = None                        # Nó raiz da árvore
        self.max_depth = max_depth              # Profundidade máxima permitida
        self.min_samples_split = min_samples_split  # Número mínimo de amostras para dividir
        self.criterium = criterium              # Critério de impureza (gini ou entropia)

    # Treinamento da árvore
    def fit(self, X_train: DataFrame, y_train: Series) -> None:
        dataset = pd.concat((X_train, y_train), axis=1)  # Une dados e rótulos
        self.root = self._build_tree(dataset)            # Constrói a árvore recursivamente

    # Constrói a árvore de forma recursiva
    def _build_tree(self, dataset: DataFrame, curr_depth: int = 0) -> DTNode:
        X_train = dataset.iloc[:, :-1]
        y_train = dataset.iloc[:, -1]
        num_samples, num_features = X_train.shape

        # Condições de parada da recursão (puro, profundidade, amostras mínimas)
        if num_samples >= self.min_samples_split and curr_depth <= self.max_depth and not self._is_pure(y_train):
            best_split = self._get_best_split(dataset)
            if best_split["info_gain"] > 0:
                children = {
                    feature_value: self._build_tree(subset, curr_depth + 1)
                    for feature_value, subset in best_split["splits"].items()
                }
                return DTNode(best_split["feature_index"], best_split["feature_name"], children, best_split["info_gain"], best_split["splits"].keys())

        # Caso base: retorna um nó folha com o valor mais comum
        leaf_value = self._calculate_leaf_value(y_train)
        return DTNode(leaf_value=leaf_value)

    # Retorna o valor mais comum (modo) para usar como folha
    def _calculate_leaf_value(self, y_train: Series) -> any:
        y_train = list(y_train)
        return max(y_train, key=y_train.count)

    # Verifica se todos os valores da coluna são iguais
    def _is_pure(self, target_column: Series) -> bool:
        return len(set(target_column)) == 1

    # Encontra o melhor atributo e divisão dos dados
    def _get_best_split(self, dataset: DataFrame) -> dict:
        best_split = {}
        max_info_gain = -float("inf")
        num_features = dataset.shape[1] - 1

        for feature_index in range(num_features):
            feature_name = dataset.columns[feature_index]
            feature_values = dataset.iloc[:, feature_index]
            splits = self._discrete_split(dataset, feature_index)

            # Calcula o ganho de informação da divisão
            info_gain = self._discrete_info_gain(dataset.iloc[:, -1], splits)

            # Atualiza se for o melhor ganho encontrado
            if info_gain > max_info_gain:
                best_split = self._update_best_split(feature_index, feature_name, info_gain, splits)
                max_info_gain = info_gain

        return best_split

    # Atualiza o dicionário com as melhores informações de split
    def _update_best_split(self, feature_index, feature_name, info_gain, splits) -> dict:
        return {
            "feature_index": feature_index,
            "feature_name": feature_name,
            "info_gain": info_gain,
            "splits": splits,
        }

    # Realiza split discreto dos dados por valor da feature
    def _discrete_split(self, dataset: DataFrame, feature_index: int) -> dict:
        splits = {}
        for feature_value in dataset.iloc[:, feature_index].unique():
            splits[feature_value] = dataset[dataset.iloc[:, feature_index] == feature_value]
        return splits

    # Calcula o ganho de informação com base nos splits
    def _discrete_info_gain(self, y_train: Series, splits: dict) -> float:
        weight_average = sum((len(subset) / len(y_train)) * self._get_impurity(subset.iloc[:, -1]) for subset in splits.values())
        return self._get_impurity(y_train) - weight_average

    # Retorna a impureza segundo o critério escolhido
    def _get_impurity(self, y_train: Series) -> float:
        return self._entropy(y_train) if self.criterium == "entropy" else self._gini_index(y_train)

    # Cálculo da entropia
    def _entropy(self, y_train: Series) -> float:
        class_labels = list(set(y_train))
        probabilities = [y_train.tolist().count(label) / len(y_train) for label in class_labels]
        return -sum(p * np.log2(p) for p in probabilities if p > 0)

    # Cálculo do índice de Gini
    def _gini_index(self, y_train: Series) -> float:
        class_labels = list(set(y_train))
        probabilities = [y_train.tolist().count(label) / len(y_train) for label in class_labels]
        return 1 - sum(p ** 2 for p in probabilities)

    # Previsões para um DataFrame de dados
    def predict(self, X_test: DataFrame) -> list:
        return [self.make_prediction(row, self.root) for _, row in X_test.iterrows()]

    # Faz a previsão para uma única amostra
    def make_prediction(self, row: tuple, node: DTNode) -> Union[any, None]:
        while node and node.leaf_value is None:
            value = row[node.feature_index]
            if value in node.children:
                node = node.children[value]
            else:
                return None  # Valor não esperado na árvore
        return node.leaf_value
    
    def predict_connect4_move(self, board: np.ndarray) -> int:
        possible_moves = game.available_moves(board)
        if not possible_moves:
            return -1  # Jogo empatado

        # Converte o tabuleiro para um formato compatível com o modelo
        flattened = board.flatten()
        df = pd.DataFrame([flattened])
        prediction = self.clf.predict(df)[0]

        # Lógica simplificada: escolhe a primeira jogada válida com melhor resultado
        for move in possible_moves:
            sim_board = game.simulate_move(board, c.PLAYER2_PIECE, move)
            sim_flattened = sim_board.flatten()
            sim_df = pd.DataFrame([sim_flattened])
            if self.clf.predict(sim_df)[0] == prediction:
                return move
        return possible_moves[0]

# Classe que encapsula o uso da árvore para diferentes domínios
class DecisionTree:
    def __init__(self, mode='iris'):
        self.mode = mode  # Modo: 'iris' ou 'connect4'
        self.clf = None   # Classificador
        self.initialize_model()

    # Inicializa o modelo conforme o modo
    def initialize_model(self):
        if self.mode == 'iris':
            self._initialize_iris_model()
        elif self.mode == 'connect4':
            self._initialize_connect4_model()

    # Inicializa modelo para o dataset Iris
    def _initialize_iris_model(self):
        try:
            self.clf = load("src/ai/models/iris.joblib")
        except FileNotFoundError:
            df = read_csv('src/ai/datasets/iris.csv')
            X = df.iloc[:, :-1]
            y = df.iloc[:, -1]
            self.clf = DecisionTreeClassifier(3, 2, "entropy")
            self.clf.fit(X, y)
            dump(self.clf, "src/ai/models/iris.joblib")

    # Inicializa modelo para o jogo Connect4
    def _initialize_connect4_model(self):
        try:
            self.clf = load("src/ai/models/connect4_dt.joblib")
        except FileNotFoundError:
            df = read_csv('src/ai/datasets/connect4_dt.csv')
            X = df.iloc[:, :-1]
            y = df.iloc[:, -1]
            self.clf = DecisionTreeClassifier(5, 2, "entropy")
            self.clf.fit(X, y)
            dump(self.clf, "src/ai/models/connect4_dt.joblib")

    # Faz a previsão para os dados da íris
    def predict_iris(self, sepal_length, sepal_width, petal_length, petal_width):
        X_test = pd.DataFrame([[sepal_length, sepal_width, petal_length, petal_width]])
        return self.clf.predict(X_test)[0]

    # Decide a melhor jogada para o jogo Connect4
    def play(self, board):
        possible_plays = game.get_possible_plays(board)
        possible_states = []
        for play in possible_plays:
            new_board = game.make_play(play, c.PLAYER1, board)
            possible_states.append((play, new_board))

        board_dicts = [game.to_dict(board) for _, board in possible_states]
        df = pd.DataFrame(board_dicts)
        predictions = self.clf.predict(df)

        # Cria um dicionário de colunas por previsão
        prediction_dict = {}
        for i, prediction in enumerate(predictions):
            if prediction not in prediction_dict:
                prediction_dict[prediction] = []
            prediction_dict[prediction].append(possible_states[i][0])

        # Prioriza vitória, depois empate, depois evitar derrota
        if c.WIN in prediction_dict:
            return random.choice(prediction_dict[c.WIN])
        elif c.DRAW in prediction_dict:
            return random.choice(prediction_dict[c.DRAW])
        elif c.LOSS in prediction_dict:
            return random.choice(prediction_dict[c.LOSS])
        else:
            return random.choice(possible_plays)
