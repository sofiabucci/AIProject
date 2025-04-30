import math
import random
from typing import Optional
from game.board import Board

class MCTSNode:
    def __init__(self, board: Board, parent: Optional['MCTSNode'] = None, move: Optional[int] = None):
        self.board = board
        self.parent = parent
        self.move = move  # Ação que levou a este nó
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = board.get_legal_moves()
    
    def uct_value(self, exploration: float = 1.41) -> float:
        """Calcula o valor UCT do nó"""
        if self.visits == 0:
            return float('inf')
        return (self.wins / self.visits) + exploration * math.sqrt(math.log(self.parent.visits) / self.visits)
    
    def select_child(self) -> 'MCTSNode':
        """Seleciona o filho com maior valor UCT"""
        return max(self.children, key=lambda child: child.uct_value())
    
    def expand(self) -> 'MCTSNode':
        """Expande um nó escolhendo um movimento não tentado"""
        move = random.choice(self.untried_moves)
        new_board = self.board.copy()
        current_player = self.get_current_player()
        new_board.drop_piece(move, current_player)
        
        child = MCTSNode(new_board, self, move)
        self.untried_moves.remove(move)
        self.children.append(child)
        return child
    
    def simulate(self) -> int:
        """Simula um jogo aleatório até o fim"""
        sim_board = self.board.copy()
        current_player = self.get_current_player()
        
        while True:
            winner = sim_board.check_winner()
            if winner is not None:
                if winner == 0:  # Empate
                    return 0
                return 1 if winner == self.get_current_player() else -1
            
            moves = sim_board.get_legal_moves()
            if not moves:
                return 0
                
            move = random.choice(moves)
            sim_board.drop_piece(move, current_player)
            current_player = 3 - current_player  # Alterna jogador
    
    def backpropagate(self, result: int):
        """Propaga o resultado da simulação para cima na árvore"""
        self.visits += 1
        self.wins += result
        if self.parent:
            self.parent.backpropagate(-result)  # Resultado é do ponto de vista do pai
    
    def get_current_player(self) -> int:
        """Determina o jogador atual"""
        counts = {1: 0, 2: 0}
        for row in self.board.state:
            for cell in row:
                if cell in counts:
                    counts[cell] += 1
        return 1 if counts[1] == counts[2] else 2

class MCTS:
    def __init__(self, board: Board, iterations: int = 1000, exploration: float = 1.41):
        self.root = MCTSNode(board)
        self.iterations = iterations
        self.exploration = exploration
    
    def search(self) -> int:
        """Executa a busca MCTS e retorna o melhor movimento"""
        for _ in range(self.iterations):
            node = self.select()
            result = self.simulate(node)
            node.backpropagate(result)
        
        return self.get_best_move()
    
    def select(self) -> MCTSNode:
        """Seleciona um nó para expandir"""
        node = self.root
        while node.children:
            node = node.select_child()
        
        if node.untried_moves:
            return node.expand()
        return node
    
    def simulate(self, node: MCTSNode) -> int:
        """Executa uma simulação a partir do nó"""
        return node.simulate()
    
    def get_best_move(self) -> int:
        """Retorna o movimento mais visitado"""
        return max(self.root.children, key=lambda child: child.visits).move