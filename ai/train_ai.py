import pandas as pd
from decision_tree import DecisionTree
import pickle
import os
import numpy as np

def load_data(filename: str = "data/connect4_training_data.csv") -> pd.DataFrame:
    """Load training data from CSV"""
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Training data file {filename} not found. Run generate_data.py first.")
    return pd.read_csv(filename)

def train_decision_tree(data: pd.DataFrame, model_file: str = "connect4_dt_model.pkl") -> DecisionTree:
    """Train and evaluate a decision tree without scikit-learn"""
    # Manual train-test split
    test_size = 0.2
    split_idx = int(len(data) * (1 - test_size))
    
    train_data = data.iloc[:split_idx]
    test_data = data.iloc[split_idx:]
    
    X_train, y_train = train_data.iloc[:, :-1], train_data.iloc[:, -1]
    X_test, y_test = test_data.iloc[:, :-1], test_data.iloc[:, -1]
    
    # Initialize and train decision tree
    print("Training Decision Tree...")
    dt = DecisionTree(max_depth=10, min_samples_split=5)
    dt.fit(X_train, y_train)
    
    # Evaluation functions
    def evaluate(X, y):
        predictions = dt.predict(X)
        correct = sum(1 for true, pred in zip(y, predictions) if abs(true - pred) < 0.5)
        return correct / len(y)
    
    train_acc = evaluate(X_train, y_train)
    test_acc = evaluate(X_test, y_test)
    
    print(f"Training accuracy: {train_acc:.2%}")
    print(f"Test accuracy: {test_acc:.2%}")
    
    # Save model
    with open(model_file, 'wb') as f:
        pickle.dump(dt, f)
    print(f"Model saved to {model_file}")
    
    return dt

if __name__ == "__main__":
    try:
        data = load_data()
        print(f"Loaded training data with {len(data)} samples")
        
        model = train_decision_tree(data)
        print("Training complete!")
    except Exception as e:
        print(f"Error: {str(e)}")