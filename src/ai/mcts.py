# Importações necessárias
import time, math, numpy as np, random
from game import constants as c  # Constantes do jogo (como valores para PLAYER1, PLAYER2, etc)
from game import rules as game  # Regras do jogo (funções como available_moves, winning_move, etc)
from ai import heuristic as h   # Heurísticas para pontuar tabuleiros simulados
from math import sqrt, log


# Classe Node representa um estado do jogo (nó na árvore de MCTS)
class Node:
    def __init__(self, board, last_player, parent=None) -> None:
        self.board = board                          # Tabuleiro atual
        self.parent = parent                        # Nó pai (nó anterior à jogada atual)
        self.children = []                          # Lista de filhos (jogadas possíveis a partir deste estado)
        self.visits = 0                             # Número de vezes que este nó foi visitado
        self.wins = 0                               # Número de vitórias associadas a este nó
        self.current_player = 1 if last_player == 2 else 2  # Define o jogador atual (alterna entre 1 e 2)

    def __str__(self) -> str:
        # Representação textual do nó para debug
        string = "Vitórias: " + str(self.wins) + '\n'
        string += "Total: " + str(self.visits) + '\n'
        string += "Pontuação: " + str(self.ucb()) + '\n'
        string += "Probabilidade de vitória: " + str(self.score()) + '\n'
        return string

    def add_children(self) -> None:
        """Adiciona todos os filhos possíveis (jogadas válidas) ao nó atual"""
        if (len(self.children) != 0) or (game.available_moves(self.board) == -1):
            return  # Não adiciona filhos se já existem ou se não há jogadas possíveis

        for col in game.available_moves(self.board):
            # Simula a jogada na coluna col para o jogador atual
            if self.current_player != c.PLAYER2_PIECE:
                copy_board = game.simulate_move(self.board, c.PLAYER2_PIECE, col)
            else:
                copy_board = game.simulate_move(self.board, c.PLAYER1_PIECE, col)

            # Cria novo nó filho com o tabuleiro simulado
            self.children.append((Node(board=copy_board, last_player=self.current_player, parent=self), col))

    def select_children(self):
        """Seleciona aleatoriamente até 4 filhos para simular"""
        if (len(self.children) > 4):
            return random.sample(self.children, 4)
        return self.children

    def ucb(self) -> float:
        """Calcula o Upper Confidence Bound (exploração + exploração) para o nó"""
        if self.visits == 0:
            return float('inf')  # Nós não visitados são priorizados
        exploitation = self.wins / self.visits
        exploration = sqrt(2) * sqrt(2 * log(self.parent.visits / self.visits, math.e)) if self.parent else 0
        return exploitation + exploration

    def score(self) -> float:
        """Retorna a taxa de vitórias (exploração)"""
        if self.visits == 0:
            return 0
        return self.wins / self.visits


# Algoritmo Monte Carlo Tree Search (MCTS)
class MCTS:
    def __init__(self, root: Node) -> None:
        self.root = root

    def start(self, max_time: int):           
        """Inicia o algoritmo: simula 6 vezes por filho antes de começar o MCTS principal"""
        self.root.add_children()

        # Pré-simulações: 6 rollouts por filho
        for child in self.root.children:
            # Se alguma jogada já for uma jogada vencedora imediata, retorna ela
            if game.winning_move(child[0].board, c.PLAYER2_PIECE):
                return child[1]
            for _ in range(6):
                result = self.rollout(child[0])
                self.back_propagation(child[0], result)

        # Inicia MCTS propriamente dito
        return self.search(max_time)

    def search(self, max_time: int) -> int:
        """Busca baseada em tempo (executa MCTS até acabar o tempo)"""
        start_time = time.time()
        while time.time() - start_time < max_time:
            selected_node = self.select(self.root)
            if selected_node.visits == 0:
                result = self.rollout(selected_node)
                self.back_propagation(selected_node, result)
            else:
                selected_children = self.expand(selected_node)
                for child in selected_children:
                    result = self.rollout(child[0])
                    self.back_propagation(child[0], result)
        return self.best_move()

    def select(self, node: Node) -> Node:
        """Seleciona recursivamente o melhor nó folha baseado no UCB"""
        if node.children == []:
            return node
        else:
            node = self.best_child(node)
            return self.select(node)

    def best_child(self, node: Node) -> Node:
        """Retorna o filho com maior UCB"""
        best_child = None
        best_score = float('-inf')
        for (child, _) in node.children:
            ucb = child.ucb()
            if ucb > best_score:
                best_child = child
                best_score = ucb
        return best_child

    def back_propagation(self, node: Node, result: int) -> None:
        """Atualiza estatísticas do nó e seus antecessores"""
        while node:
            node.visits += 1
            if node.current_player == result:  # Se o jogador atual ganhou a simulação
                node.wins += 1
            node = node.parent

    def expand(self, node: Node):
        """Expande o nó atual e retorna até 4 filhos selecionados aleatoriamente"""
        node.add_children()
        return node.select_children()

    def rollout(self, node: Node) -> int:
        """Simula uma partida completa a partir do estado atual até o fim"""
        board = node.board.copy()
        current_player = node.current_player

        while True:
            if game.winning_move(board, 1):
                return 1
            if game.winning_move(board, 2):
                return 2
            if game.is_game_tied(board):
                return 0

            moves = game.available_moves(board)
            if moves == -1:
                return 0

            move_scores = []
            for move in moves:
                sim_board = game.simulate_move(board, current_player, move)
                if game.winning_move(sim_board, current_player):
                    return current_player  # Ganhou diretamente
                # Avalia o tabuleiro usando heurística
                score = h.calculate_board_score(sim_board, current_player, 1 if current_player == 2 else 2)
                move_scores.append(score)

            total = sum(move_scores)
            if total <= 0:
                move = random.choice(moves)
            else:
                weights = [s / total for s in move_scores]
                move = random.choices(moves, weights=weights, k=1)[0]

            # Atualiza tabuleiro e alterna jogador
            board = game.simulate_move(board, current_player, move)
            current_player = 1 if current_player == 2 else 2

    def best_move(self) -> int:
        """Escolhe a melhor jogada com base na maior taxa de vitórias"""
        max_score = float('-inf')
        scores = {}
        columns = []

        for (child, col) in self.root.children:
            score = child.score()
            print(f"Coluna: {col}")
            print(child)
            if score > max_score:
                max_score = score
            scores[col] = score

        for col, score in scores.items():
            if score == max_score:
                columns.append(col)

        return random.choice(columns)  # Em caso de empate, escolhe aleatoriamente


# Função que executa o algoritmo dado um tabuleiro
def mcts(board: np.ndarray) -> int:
    """Retorna a melhor jogada para o tabuleiro dado"""
    root = Node(board=board, last_player=c.PLAYER2_PIECE)
    mcts = MCTS(root)
    column = mcts.start(3)  # Executa por 3 segundos
    print(column + 1)  # Para debug (colunas indexadas a partir de 1)
    return column
