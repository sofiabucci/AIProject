import math
import pandas as pd
from typing import Dict, List, Optional, Union
from game.board import Board
from collections import Counter

class DecisionTree:
    """
    Decision Tree implementation using ID3 algorithm
    """
    def __init__(self, max_depth: Optional[int] = None, 
                 min_samples_split: int = 2):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.tree = None
    
    def fit(self, X: pd.DataFrame, y: pd.Series) -> None:
        """
        Build decision tree from training data
        """
        dataset = pd.concat([X, y], axis=1)
        self.tree = self._build_tree(dataset, depth=0)
    
    def _build_tree(self, dataset: pd.DataFrame, depth: int) -> Dict:
        """
        Recursively build the decision tree
        """
        X, y = dataset.iloc[:, :-1], dataset.iloc[:, -1]
        
        # Stopping conditions
        if (self.max_depth is not None and depth >= self.max_depth) or \
           len(y) < self.min_samples_split or \
           len(set(y)) == 1:
            return self._create_leaf_node(y)
        
        best_split = self._find_best_split(dataset)
        
        if best_split["info_gain"] <= 0:
            return self._create_leaf_node(y)
        
        left_subtree = self._build_tree(best_split["dataset_left"], depth+1)
        right_subtree = self._build_tree(best_split["dataset_right"], depth+1)
        
        return {
            "feature_index": best_split["feature_index"],
            "threshold": best_split["threshold"],
            "left": left_subtree,
            "right": right_subtree
        }
    
    def _find_best_split(self, dataset: pd.DataFrame) -> Dict:
        """
        Find the best split for a dataset
        """
        best_split = {}
        max_info_gain = -float("inf")
        
        for feature_idx in range(dataset.shape[1]-1):
            feature_values = dataset.iloc[:, feature_idx]
            unique_values = sorted(set(feature_values))
            
            for threshold in unique_values:
                dataset_left = dataset[dataset.iloc[:, feature_idx] <= threshold]
                dataset_right = dataset[dataset.iloc[:, feature_idx] > threshold]
                
                if len(dataset_left) > 0 and len(dataset_right) > 0:
                    info_gain = self._information_gain(
                        dataset.iloc[:, -1], dataset_left.iloc[:, -1], dataset_right.iloc[:, -1])
                    
                    if info_gain > max_info_gain:
                        best_split = {
                            "feature_index": feature_idx,
                            "threshold": threshold,
                            "dataset_left": dataset_left,
                            "dataset_right": dataset_right,
                            "info_gain": info_gain
                        }
                        max_info_gain = info_gain
        
        return best_split
    
    def _information_gain(self, parent: pd.Series, 
                        left_child: pd.Series, 
                        right_child: pd.Series) -> float:
        """
        Calculate information gain for a split
        """
        weight_left = len(left_child) / len(parent)
        weight_right = len(right_child) / len(parent)
        return self._entropy(parent) - (
            weight_left * self._entropy(left_child) + weight_right * self._entropy(right_child))
    
    def _entropy(self, y: pd.Series) -> float:
        """
        Calculate entropy of a target variable
        """
        class_counts = Counter(y)
        entropy = 0.0
        total = len(y)
        
        for count in class_counts.values():
            p = count / total
            entropy += -p * math.log2(p)
        
        return entropy
    
    def _create_leaf_node(self, y: pd.Series) -> Dict:
        """
        Create a leaf node with the most common class
        """
        class_counts = Counter(y)
        return {
            "class": max(class_counts.items(), key=lambda x: x[1])[0],
            "samples": len(y)
        }
    
    def predict(self, X: pd.DataFrame) -> List:
        """
        Make predictions for input data
        """
        return [self._predict_single(x, self.tree) for _, x in X.iterrows()]
    
    def _predict_single(self, x: pd.Series, tree: Dict) -> Union[int, str]:
        """
        Predict class for a single sample
        """
        if "class" in tree:
            return tree["class"]
        
        if x[tree["feature_index"]] <= tree["threshold"]:
            return self._predict_single(x, tree["left"])
        return self._predict_single(x, tree["right"])

class DecisionTreeAgent:
    """
    Decision Tree agent for Connect Four
    """
    def __init__(self, model: Optional[DecisionTree] = None):
        self.model = model
    
    def train_iris(self, filepath: str) -> None:
        """
        Train on Iris dataset with discretization
        """
        df = pd.read_csv(filepath)
        X = df.iloc[:, :-1]
        y = df.iloc[:, -1]
        
        # Discretize features
        for col in X.columns:
            X[col] = pd.cut(X[col], bins=5, labels=False)
        
        self.model = DecisionTree(max_depth=4)
        self.model.fit(X, y)
    
    def train_connect4(self, filepath: str) -> None:
        """
        Train on Connect Four dataset
        """
        df = pd.read_csv(filepath)
        X = df.iloc[:, :-1]
        y = df.iloc[:, -1]
        
        self.model = DecisionTree(max_depth=10)
        self.model.fit(X, y)
    
    def get_best_move(self, board: 'Board') -> int:
        if not self.model:
            raise ValueError("Model not trained")
        
        valid_moves = [col for col in range(board.columns) if board.is_valid_move(col)]
        if not valid_moves:
            raise ValueError("No valid moves available")
        
        # Predict the best move among valid moves
        best_move = None
        best_score = -float('inf')
        for move in valid_moves:
            # Simulate making the move and create a feature vector
            simulated_board = board.simulate_move(move)
            features = pd.DataFrame([simulated_board.to_feature_vector()])
            predicted_score = self.model.predict(features)[0]
            if predicted_score > best_score:
                best_score = predicted_score
                best_move = move
        return best_move