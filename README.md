# Connect 4 
### **Project Presentation**

#### **Project Objective**
The goal of this project was to develop a program capable of playing **Connect Four** against human players or other algorithms, using:

1. **Monte Carlo Tree Search (MCTS)** with **UCT (Upper Confidence Bound for Trees)**.
2. **Decision Trees** built using the **ID3 algorithm**.

---

### **1. Connect Four Game Implementation**

* **Supported Game Modes**:
  * Human vs. Human
  * Human vs. Computer
  * Computer vs. Computer (using two different algorithms, in which we chose the second one to be A*)

---

### **2. Monte Carlo Tree Search (MCTS) Implementation**

* **Key Features**:
  * Implemented the **MCTS algorithm** with **UCT** for balanced exploration and exploitation.
  * Evaluated different numbers of child nodes selected per parent node to optimize performance.
  * Used **heuristic-guided simulations** to improve decision-making efficiency.
  * Set a **3-second time limit** per move to balance speed and accuracy.
---

### **3. Decision Trees with ID3 Algorithm**

* **Dataset 1: Iris Dataset**  
  * **Provided on Moodle** (standard machine learning dataset).  
  * **Preprocessing**:  
    - Discretized numerical features (sepal/petal length and width).  
    - Trained a decision tree using **entropy-based splitting**.  
  * **Application**:  
    - Classified iris flowers into three species (setosa, versicolor, virginica).  

* **Dataset 2: Connect Four Game States**  
  * **Generated using MCTS**:  
    - Simulated thousands of game states to create pairs of **(current board state, optimal move)**.  
    - Each state represented as a flattened 42-position array (6x7 grid).  
  * **Decision Tree Training**:  
    - Used **ID3 with entropy minimization**.  
    - Limited tree depth to **5 levels** to prevent overfitting.  
  * **Functionality**:  
    - Predicts the next optimal move given a board state.  
    - Operates in **under 0.05 seconds per move**, making it the fastest algorithm.  


## Installation

**Prerequisites:**

- Python 3.x (https://www.python.org/downloads/)
- pip (package installer for Python - usually included with Python installation)

**Installing Dependencies:**

1. Open your terminal or command prompt.
2. Navigate to the project directory using the `cd` command.
3. Run the following command to install required dependencies listed in `requirements.txt`:

```
pip install -r requirements.txt
```

**Running the game**
1. Open your terminal or command prompt.
2. Navigate to the project directory using the `cd` command.
3. Run the following command to play the game.

```
python3 main.py
```
<hr>

<img src="./assets/inicio.png">
<img src="./assets/modos.png">
<img src="./assets/final.png">

