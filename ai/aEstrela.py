import math
from collections import deque
import random
import heapq

class AStar:
    def __init__(self, initial_state, player):
        self.initial_state = initial_state
        self.player = player  # O jogador que está usando o A* (1 ou 2)
        self.opponent = 3 - player  # Oponente (2 ou 1)

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
        score = 0
        
        # Avalia todas as possíveis sequências de 4 células
        for r in range(6):
            for c in range(7):
                # Verifica horizontal
                if c <= 3:
                    segment = [state[r][c+i] for i in range(4)]
                    score += self.evaluate_segment(segment)
                # Verifica vertical
                if r <= 2:
                    segment = [state[r+i][c] for i in range(4)]
                    score += self.evaluate_segment(segment)
                # Verifica diagonal ascendente
                if r <= 2 and c <= 3:
                    segment = [state[r+i][c+i] for i in range(4)]
                    score += self.evaluate_segment(segment)
                # Verifica diagonal descendente
                if r >= 3 and c <= 3:
                    segment = [state[r-i][c+i] for i in range(4)]
                    score += self.evaluate_segment(segment)
        
        return score

    def evaluate_segment(self, segment):
        """Avalia um segmento de 4 células."""
        player_count = segment.count(self.player)
        opponent_count = segment.count(self.opponent)
        
        if player_count == 4:
            return 1000  # Vitória
        if opponent_count == 4:
            return -1000  # Derrota
        
        # Pontuações heurísticas
        if player_count == 3 and opponent_count == 0:
            return 100  # Quase vitória
        if player_count == 2 and opponent_count == 0:
            return 10   # Boa posição
        if player_count == 1 and opponent_count == 0:
            return 1    # Posição neutra
        if opponent_count == 3 and player_count == 0:
            return -100 # Quase derrota
        if opponent_count == 2 and player_count == 0:
            return -10  # Má posição
        if opponent_count == 1 and player_count == 0:
            return -1   # Posição neutra desfavorável
        
        return 0  # Segmento misto ou vazio

    def search(self, max_depth=5):
        """Executa a busca A* para encontrar a melhor jogada."""
        open_set = []
        # Cada elemento é (f_score, g_score, state, action_path)
        initial_g = 0
        initial_h = self.evaluate(self.initial_state)
        heapq.heappush(open_set, (initial_g + initial_h, initial_g, self.initial_state, []))
        
        best_score = -math.inf
        best_action = None
        
        while open_set:
            current_f, current_g, current_state, action_path = heapq.heappop(open_set)
            
            # Se atingirmos a profundidade máxima ou o jogo terminar
            if len(action_path) >= max_depth or self.is_terminal(current_state):
                current_score = self.evaluate(current_state)
                if current_score > best_score:
                    best_score = current_score
                    if action_path:
                        best_action = action_path[0]
                continue
            
            # Expande o estado atual
            for action in self.get_legal_actions(current_state):
                new_state = self.apply_action(current_state, action, self.player)
                new_action_path = action_path + [action]
                new_g = current_g + 1  # Custo do caminho aumenta em 1
                new_h = self.evaluate(new_state)
                new_f = new_g + new_h
                
                heapq.heappush(open_set, (new_f, new_g, new_state, new_action_path))
        
        # Se não encontrou nenhuma ação (teoricamente impossível no Connect 4)
        return best_action if best_action is not None else random.choice(self.get_legal_actions(self.initial_state))