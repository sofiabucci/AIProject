from typing import Union
import numpy as np
import pandas as pd
import random
from pandas import DataFrame, Series, read_csv
from game import rules as game
from game import constants as c
from joblib import load, dump

been_called = False

class DTNode:
    def __init__(self, feature_index=None, feature_name=None, children=None, info_gain=None, split_values = None, leaf_value=None) -> None:
        self.feature_index = feature_index   
        self.feature_name = feature_name      
        self.children = children
        self.info_gain = info_gain 
        self.split_values = split_values 
        self.leaf_value = leaf_value 


class DecisionTreeClassifier:
    def __init__(self, max_depth: int = None, min_samples_split: int = None, criterium: str = 'entropy') -> None:
        self.root: DTNode = None
        self.max_depth: int = max_depth 
        self.min_samples_split: int = min_samples_split 
        self.criterium: str = criterium

    

    def fit(self, X_train: DataFrame, y_train: Series) -> None:
        '''Fit the tree with a DataFrame for trainning'''
        dataset = pd.concat((X_train, y_train), axis=1)
        self.root = self._build_tree(dataset)



    def _build_tree(self, dataset: DataFrame, curr_depth: int = 0) -> DTNode:
        '''Construct the Decision Tree from the root node''' 
        print(curr_depth)
        X_train, y_train = dataset.iloc[:,:-1], dataset.iloc[:,-1]
        num_samples = X_train.shape[0]
        
        if num_samples<self.min_samples_split or curr_depth==self.max_depth or self._is_pure(y_train): 
            return DTNode(leaf_value=self._calculate_leaf_value(y_train))
        
        best_split = self._get_best_split(dataset) 
        if best_split == {}: 
            return DTNode(leaf_value=self._calculate_leaf_value(y_train)) 

        children = []
        for child in best_split["children"]:
            children.append(self._build_tree(child, curr_depth+1))
        return DTNode(best_split["feature_index"], best_split["feature_name"], children, best_split["info_gain"], best_split["split_values"])


    
    def _calculate_leaf_value(self, y_train: Series) -> any: 
        '''Get value of the majority of results in a leaf node'''
        list_y = list(y_train)
        max_count = max(list_y.count(item) for item in set(list_y)) 
        most_common_values = [item for item in set(list_y) if list_y.count(item) == max_count] 
        return random.choice(most_common_values)
    


    def _is_pure(self, target_column: Series) -> bool:
        '''Check if a node have only one type of target value'''
        return len(set(target_column)) == 1
    


    def _get_best_split(self, dataset: DataFrame) -> dict:
        '''Get the best split for a node'''
        best_split = {}
        max_info_gain = 0
        y_train = dataset.iloc[:, -1]
        train_columns = dataset.shape[1] - 1 

        for feature_index in range(train_columns):
            # if max_info_gain > 0.3: break
            feature_name = dataset.columns[feature_index]       
            values = dataset.iloc[:, feature_index]    

            children, info_gain = self._discrete_split(dataset, feature_index, pd.unique(values), y_train)
            max_info_gain = self._update_best_split(best_split, info_gain, max_info_gain, children, pd.unique(values), feature_name, feature_index)
        return best_split
    


    def _update_best_split(self, best_split: dict, info_gain: float, max_info_gain: float, children: list, value: any, feature_name: str, feature_index: int) -> float:
        if info_gain > max_info_gain:
            best_split["feature_index"] = feature_index
            best_split["feature_name"] = feature_name
            best_split["split_values"] = value
            best_split["children"] = children
            best_split["info_gain"] = info_gain
            return info_gain
        return max_info_gain
    


    def _discrete_split(self, dataset: DataFrame, feature_index: int, values: Series, y_parent: Series) -> tuple[list, float]:
        '''Split the DataFrame with a discrete and multiclass value'''
        labels = pd.unique(values)
        children = []
        for label in labels:
            child_dataset = dataset[dataset.iloc[:, feature_index] == label]
            children.append(child_dataset)
        info_gain = self._discrete_info_gain(dataset, children, y_parent)
        return children, info_gain



    def _discrete_info_gain(self, parent_dataset: DataFrame, children: list, y_parent) -> float:
        '''Get the information gain for a node splitted by a multiclass discrete value'''
        children_impurity_sum = 0
        for child_dataset in children:
            children_impurity_sum += child_dataset.shape[0] / parent_dataset.shape[0] * self._get_impurity(child_dataset.iloc[:, -1])
        return self._get_impurity(y_parent) - children_impurity_sum



    def _get_impurity(self, y_train: Series) -> float:
        '''Get the impority of the node'''
        return self._gini_index(y_train) if self.criterium=='gini' else self._entropy(y_train)



    def _entropy(self, y_train: Series) -> float:
        '''Get the entropy value for a node'''
        class_labels = pd.unique(y_train)
        entropy = 0
        for label in class_labels:
            label_positives = len(y_train[y_train == label]) / len(y_train)
            entropy += -(label_positives * np.log2(label_positives))
        return entropy
    


    def _gini_index(self, y_train: Series) -> float:
        '''Get the gini value for a node'''
        class_labels = pd.unique(y_train)
        gini = 0
        for label in class_labels:
            label_positives = len(y_train[y_train == label]) / len(y_train)
            gini += label_positives**2
        return 1 - gini



    def predict(self, X_test: DataFrame) -> list:
        '''Predict target column for a dataframe'''
        return [self.make_prediction(row, self.root) for _, row in X_test.iterrows()]



    def make_prediction(self, row: tuple, node: DTNode) -> Union[any, None]:
        '''Predict target for each row in dataframe'''
        if node.leaf_value is not None: 
            return node.leaf_value
        
        index = node.feature_index
        attribute = node.feature_name
        value = row[index]

        for i, node_value in enumerate(node.split_values):
            if value == node_value:
                return self.make_prediction(row, node.children[i])  

        return None
    
class DecisionTree:
    def __init__(self, mode='iris'):
        """
        Initialize Decision Tree for either iris classification or connect4 game
        
        Parameters:
        - mode: 'iris' for iris dataset classification or 'connect4' for game moves
        """
        self.mode = mode
        self.model = None
        self.initialize_model()
    
    def initialize_model(self):
        """Load or train the appropriate model based on mode"""
        if self.mode == 'iris':
            self._initialize_iris_model()
        elif self.mode == 'connect4':
            self._initialize_connect4_model()
        else:
            raise ValueError("Mode must be either 'iris' or 'connect4'")

    def _initialize_iris_model(self):
        """Handle iris dataset model initialization"""
        try:
            self.model = load('datasets/iris_dt.joblib')
        except:
            # Load and preprocess iris dataset
            df = read_csv('datasets/iris.csv')
            target = df['class']
            features = df.drop(['class', 'ID'], axis=1)
            
            # Train decision tree with more reasonable parameters
            self.model = DecisionTreeClassifier(max_depth=5, min_samples_split=5)
            self.model.fit(features, target)
            
            # Save trained model
            dump(self.model, 'datasets/iris_dt.joblib')

    def _initialize_connect4_model(self):
        """Handle connect4 game model initialization"""
        try:
            self.model = load('datasets/connect4_dataset.joblib')
        except:
            # Load and preprocess connect4 dataset
            df = read_csv('datasets/connect4_dataset.csv')
            target = df['move']
            features = df.drop(['move'], axis=1)
            
            # Train decision tree with game-appropriate parameters
            self.model = DecisionTreeClassifier(max_depth=10, min_samples_split=20)
            self.model.fit(features, target)
            
            # Save trained model
            dump(self.model, 'datasets/connect4_dataset.joblib')

    def predict_iris(self, sepal_length, sepal_width, petal_length, petal_width):
        """
        Predict iris flower type based on features
        
        Parameters:
        - sepal_length, sepal_width, petal_length, petal_width: flower measurements
        
        Returns:
        - Predicted iris class (e.g., 'Iris-setosa')
        """
        if self.mode != 'iris':
            raise RuntimeError("This model was initialized for connect4, not iris classification")
            
        input_data = pd.DataFrame({
            'sepallength': [sepal_length],
            'sepalwidth': [sepal_width],
            'petallength': [petal_length],
            'petalwidth': [petal_width]
        })
        return self.model.predict(input_data)[0]

    def play(self, board):
        """
        Determine best move for connect4 game
        
        Parameters:
        - board: 2D array representing current game state
        
        Returns:
        - Column index for best move
        """
        if self.mode != 'connect4':
            raise RuntimeError("This model was initialized for iris classification, not connect4")
            
        available_moves = game.available_moves(board)
        best_moves = []
        average_moves = []
        worst_moves = []

        for col in available_moves:
            temp_board = game.simulate_move(board, c.AI_PIECE, col)
            row = self._map_board_to_row(temp_board)
            prediction = self.model.predict(row)
            
            # Assuming predictions are 'win', 'draw', 'loss' from the dataset
            if prediction[0] == 'win':
                worst_moves.append(col)
            elif prediction[0] == 'draw':
                average_moves.append(col)
            elif prediction[0] == 'loss':
                best_moves.append(col)

        # Decision logic - prefer moves that lead to opponent's loss (our win)
        if best_moves:
            return random.choice(best_moves)
        elif average_moves:
            return random.choice(average_moves)
        return random.choice(worst_moves) if worst_moves else random.choice(available_moves)

    def _map_board_to_row(self, board):
        """Convert connect4 board state to dataframe row format"""
        flattened = [item for sublist in board for item in sublist]
        result = pd.DataFrame([flattened])
        result.replace({0: 'b', 1: 'x', 2: 'o'}, inplace=True)  # b=blank, x=player, o=AI
        return result