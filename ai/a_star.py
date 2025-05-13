import math
from collections import deque
from typing import Optional
import random
import pandas as pd
import heapq
from decision_tree import DecisionTreeAgent

class AStar:
    def __init__(self, initial_state, player, decision_tree_agent: Optional[DecisionTreeAgent] = None):
        self.initial_state = initial_state
        self.player = player  # O jogador que está usando o A* (1 ou 2)
        self.opponent = 3 - player  # Oponente (2 ou 1)
        self.decision_tree_agent = decision_tree_agent

    def get_legal_actions(self, state):
        """Retorna as colunas disponíveis para jogar."""
        return [col for col in range(7) if state[0][col] == 0]

    def apply_action(self, state, action, player):
        """Aplica uma ação (jogar em uma coluna) e retorna o novo estado."""
        new_state = [row[:] for row in state]
        for row in range(5, -1, -1):
            if new_state[row][action] == 0:
                new_state[row][action] = player
                break
        return new_state

    def is_terminal(self, state):
        """Verifica se o jogo terminou (vitória ou empate)."""
        # Verifica vitória
        rows, cols = 6, 7
        for r in range(rows):
            for c in range(cols):
                player = state[r][c]
                if player == 0:
                    continue
                # Horizontal
                if c <= cols - 4 and all(state[r][c + i] == player for i in range(4)):
                    return True
                # Vertical
                if r <= rows - 4 and all(state[r + i][c] == player for i in range(4)):
                    return True
                # Diagonal ascendente
                if r <= rows - 4 and c <= cols - 4 and all(state[r + i][c + i] == player for i in range(4)):
                    return True
                # Diagonal descendente
                if r >= 3 and c <= cols - 4 and all(state[r - i][c + i] == player for i in range(4)):
                    return True

        # Verifica empate
        if all(state[0][col] != 0 for col in range(cols)):
            return True

        return False

    def evaluate(self, state):
        """Função de avaliação heurística para o estado atual."""
        if self.decision_tree_agent:
            # Convert state to feature vector (you'll need to implement this)
            features = self._state_to_feature_vector(state)
            score = self.decision_tree_agent.model.predict(pd.DataFrame([features]))[0]
            return score
        else:
            # Fallback to original heuristic
            score = 0
            for r in range(6):
                for c in range(7):
                    if c <= 3:
                        segment = [state[r][c+i] for i in range(4)]
                        score += self.evaluate_segment(segment)
                    if r <= 2:
                        segment = [state[r+i][c] for i in range(4)]
                        score += self.evaluate_segment(segment)
                    if r <= 2 and c <= 3:
                        segment = [state[r+i][c+i] for i in range(4)]
                        score += self.evaluate_segment(segment)
                    if r >= 3 and c <= 3:
                        segment = [state[r-i][c+i] for i in range(4)]
                        score += self.evaluate_segment(segment)
            return score

    def _state_to_feature_vector(self, state):
        """Convert the game state to a feature vector for DecisionTree"""
        # Implement this based on how your DecisionTree expects features
        # This is just a placeholder - you'll need to adapt it to your actual features
        features = []
        for row in state:
            for cell in row:
                features.append(cell)
        return features

    def evaluate_segment(self, segment):
        """Avalia um segmento de 4 células."""
        player_count = segment.count(self.player)
        opponent_count = segment.count(self.opponent)
        
        if player_count == 4:
            return 1000
        if opponent_count == 4:
            return -1000
        if player_count == 3 and opponent_count == 0:
            return 100
        if player_count == 2 and opponent_count == 0:
            return 10
        if player_count == 1 and opponent_count == 0:
            return 1
        if opponent_count == 3 and player_count == 0:
            return -100
        if opponent_count == 2 and player_count == 0:
            return -10
        if opponent_count == 1 and player_count == 0:
            return -1
        return 0

    def search(self, max_depth=5):
        """Executa a busca A* para encontrar a melhor jogada."""
        open_set = []
        initial_g = 0
        initial_h = self.evaluate(self.initial_state)
        heapq.heappush(open_set, (initial_g + initial_h, initial_g, self.initial_state, []))
        
        best_score = -math.inf
        best_action = None
        
        while open_set:
            current_f, current_g, current_state, action_path = heapq.heappop(open_set)
            
            if len(action_path) >= max_depth or self.is_terminal(current_state):
                current_score = self.evaluate(current_state)
                if current_score > best_score:
                    best_score = current_score
                    if action_path:
                        best_action = action_path[0]
                continue
            
            for action in self.get_legal_actions(current_state):
                new_state = self.apply_action(current_state, action, self.player)
                new_action_path = action_path + [action]
                new_g = current_g + 1
                new_h = self.evaluate(new_state)
                new_f = new_g + new_h
                
                heapq.heappush(open_set, (new_f, new_g, new_state, new_action_path))
        
        return best_action if best_action is not None else random.choice(self.get_legal_actions(self.initial_state))