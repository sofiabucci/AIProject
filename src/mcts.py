import random
import math

class Node:
    def __init__(self, state, parent=None):
        self.state = state  # Estado do jogo
        self.parent = parent  # Nó pai
        self.children = []  # Nós filhos
        self.wins = 0  # Número de vitórias nas simulações
        self.visits = 0  # Número de visitas ao nó
        self.untried_actions = self.get_legal_actions()  # Ações não exploradas

    def get_legal_actions(self):
        # Retorna as ações legais (colunas disponíveis)
        return [col for col in range(7) if self.state[0][col] == 0]

    def select_child(self):
        # Seleciona o filho com o maior valor UCT
        return max(self.children, key=lambda c: c.wins / c.visits + math.sqrt(2 * math.log(self.visits) / c.visits))

    def add_child(self, action):
        # Cria um novo nó filho a partir de uma ação
        new_state = self.simulate_action(self.state, action)
        child = Node(new_state, self)
        self.children.append(child)
        return child

    def simulate_action(self, state, action):
        # Simula a ação no estado atual e retorna o novo estado
        new_state = [row[:] for row in state]
        for row in range(5, -1, -1):
            if new_state[row][action] == 0:
                new_state[row][action] = self.get_current_player()
                break
        return new_state

    def get_current_player(self):
        # Retorna o jogador atual (1 ou 2)
        return 1 if sum(row.count(1) for row in self.state) <= sum(row.count(2) for row in self.state) else 2

class MCTS:
    def __init__(self, root_state):
        self.root = Node(root_state)

    def search(self, iterations):
        for _ in range(iterations):
            node = self.select()  # Seleção
            if not node.untried_actions:
                node = node.select_child()
            reward = self.simulate(node)  # Simulação
            self.backpropagate(node, reward)  # Retropropagação

    def select(self):
        # Seleciona o nó a ser expandido
        current = self.root
        while current.children:
            current = current.select_child()
        return current

    def simulate(self, node):
        # Simula uma partida aleatória a partir do nó
        state = node.state
        while not self.is_terminal(state):
            action = random.choice(self.get_legal_actions(state))
            state = self.simulate_action(state, action)
        return self.get_reward(state)

    def backpropagate(self, node, reward):
        # Retropropaga o resultado da simulação
        while node:
            node.visits += 1
            node.wins += reward
            node = node.parent

    def get_best_action(self):
        # Retorna a ação com mais visitas
        return max(self.root.children, key=lambda c: c.visits).state