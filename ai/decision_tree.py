import math
import pandas as pd
from typing import Dict, List, Optional, Union
from game.board import Board
from collections import Counter
import numpy as np

class DecisionTree:
    """
    Enhanced Decision Tree implementation optimized for Connect Four heuristic evaluation
    """
    def __init__(self, max_depth: Optional[int] = None, 
                 min_samples_split: int = 5,  # Increased for more stable splits
                 heuristic_mode: bool = True):  # Added flag for heuristic mode
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.heuristic_mode = heuristic_mode
        self.tree = None
    
    def fit(self, X: pd.DataFrame, y: pd.Series) -> None:
        """
        Build decision tree from training data with Connect Four specific adjustments
        """
        if self.heuristic_mode:
            # For heuristic mode, we want regression-style predictions
            # Discretize the target variable into bins for classification
            y = pd.cut(y, bins=10, labels=False)
        
        dataset = pd.concat([X, y], axis=1)
        self.tree = self._build_tree(dataset, depth=0)
    
    def _build_tree(self, dataset: pd.DataFrame, depth: int) -> Dict:
        """
        Recursively build the decision tree with Connect Four optimizations
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
        Find the best split for a dataset with Connect Four specific features
        """
        best_split = {}
        max_info_gain = -float("inf")
        
        # Prioritize board position features first
        feature_priority = sorted(range(dataset.shape[1]-1), 
                              key=lambda i: "pos" in dataset.columns[i])
        
        for feature_idx in feature_priority:
            feature_values = dataset.iloc[:, feature_idx]
            unique_values = sorted(set(feature_values))
            
            # Evaluate fewer thresholds for speed
            for threshold in np.linspace(min(unique_values), max(unique_values), num=5):
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
        Calculate information gain with smoothing for stability
        """
        weight_left = len(left_child) / len(parent)
        weight_right = len(right_child) / len(parent)
        gain = self._entropy(parent) - (
            weight_left * self._entropy(left_child) + weight_right * self._entropy(right_child))
        return max(gain, 0)  # Ensure no negative gains
    
    def _entropy(self, y: pd.Series) -> float:
        """
        Calculate entropy with Laplace smoothing
        """
        class_counts = Counter(y)
        entropy = 0.0
        total = len(y)
        
        for count in class_counts.values():
            p = (count + 1) / (total + len(class_counts))  # Laplace smoothing
            entropy += -p * math.log2(p + 1e-10)  # Small epsilon to avoid log(0)
        
        return entropy
    
    def _create_leaf_node(self, y: pd.Series) -> Dict:
        """
        Create a leaf node that can return both class and value
        """
        class_counts = Counter(y)
        if self.heuristic_mode:
            # For heuristic mode, return mean value
            return {
                "value": y.mean(),
                "samples": len(y)
            }
        else:
            return {
                "class": max(class_counts.items(), key=lambda x: x[1])[0],
                "samples": len(y)
            }
    
    def predict(self, X: pd.DataFrame) -> List:
        """
        Make predictions for input data, returning continuous values in heuristic mode
        """
        return [self._predict_single(x, self.tree) for _, x in X.iterrows()]
    
    def _predict_single(self, x: pd.Series, tree: Dict) -> Union[int, float]:
        """
        Predict value for a single sample
        """
        if "value" in tree:
            return tree["value"]
        if "class" in tree:
            return tree["class"]
        
        if x[tree["feature_index"]] <= tree["threshold"]:
            return self._predict_single(x, tree["left"])
        return self._predict_single(x, tree["right"])

class DecisionTreeAgent:
    """
    Enhanced Decision Tree agent for Connect Four with board evaluation features
    """
    def __init__(self, model: Optional[DecisionTree] = None):
        self.model = model or DecisionTree(max_depth=10, heuristic_mode=True)
    
    def train_connect4(self, filepath: str) -> None:
        """
        Train on Connect Four dataset with specialized feature engineering
        """
        df = pd.read_csv(filepath)
        
        # Feature engineering specific to Connect Four
        X = self._extract_features(df.iloc[:, :-1])
        y = df.iloc[:, -1]  # Assuming last column is outcome (win/loss/score)
        
        self.model.fit(X, y)
    
    def _extract_features(self, raw_features: pd.DataFrame) -> pd.DataFrame:
        """
        Extract meaningful Connect Four features from raw board positions
        """
        features = pd.DataFrame()
        
        # Example features (adapt based on your actual data structure):
        # 1. Count of potential winning paths
        features['my_3_in_row'] = raw_features.apply(lambda row: self._count_threats(row, player=1, length=3), axis=1)
        features['opp_3_in_row'] = raw_features.apply(lambda row: self._count_threats(row, player=2, length=3), axis=1)
        
        # 2. Center control
        features['center_control'] = raw_features.apply(lambda row: self._center_control(row), axis=1)
        
        # 3. Potential forks
        features['potential_forks'] = raw_features.apply(lambda row: self._count_forks(row), axis=1)
        
        return features
    
    def _count_threats(self, board_state, player, length):
        """Count how many open lines of given length exist for player"""
        # Implement board-specific threat detection
        return 0  # Placeholder
    
    def _center_control(self, board_state):
        """Measure control of center columns"""
        # Implement center control calculation
        return 0  # Placeholder
    
    def _count_forks(self, board_state):
        """Count potential fork opportunities"""
        # Implement fork detection
        return 0  # Placeholder
    
    def evaluate_board(self, board: Board) -> float:
        """
        Evaluate a board position using the decision tree
        """
        if not self.model:
            raise ValueError("Model not trained")
        
        features = self._board_to_features(board)
        return self.model.predict(pd.DataFrame([features]))[0]
    
    def _board_to_features(self, board: Board) -> dict:
        """
        Convert a game board to features for the decision tree
        """
        # Implement conversion from Board object to feature dictionary
        # This should match the features used in training
        return {
            'my_3_in_row': board.count_connected(board.current_player, 3),
            'opp_3_in_row': board.count_connected(3 - board.current_player, 3),
            'center_control': self._calculate_center_control(board),
            # Add other relevant features
        }
    
    def _calculate_center_control(self, board: Board) -> float:
        """Calculate center control metric for current player"""
        center_columns = [2, 3, 4]  # Middle columns in Connect Four
        control = 0
        for col in center_columns:
            for row in range(6):
                if board.grid[row][col] == board.current_player:
                    control += 1
                elif board.grid[row][col] != 0:
                    control -= 1
        return control