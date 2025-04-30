from typing import Optional
from game.board import Board

class CLIGame:
    def __init__(self, player1, player2):
        self.board = Board()
        self.players = {1: player1, 2: player2}
    
    def play(self):
        """Executa o jogo até o fim"""
        current_player = 1
        
        while True:
            print("\n" + str(self.board))
            winner = self.board.check_winner()
            
            if winner is not None:
                if winner == 0:
                    print("\nEmpate!")
                else:
                    print(f"\nJogador {winner} venceu!")
                break
            
            move = self.players[current_player].get_move(self.board)
            if move is None:  # Jogador desistiu
                print(f"\nJogador {current_player} desistiu!")
                winner = 3 - current_player
                break
                
            self.board.drop_piece(move, current_player)
            current_player = 3 - current_player  # Alterna jogador

class HumanPlayer:
    def get_move(self, board: Board) -> Optional[int]:
        """Obtém movimento do jogador humano"""
        while True:
            try:
                move = input(f"Escolha uma coluna (0-{Board.COLS-1}) ou 'q' para sair: ")
                if move.lower() == 'q':
                    return None
                
                move = int(move)
                if board.is_valid_move(move):
                    return move
                print("Movimento inválido. Tente novamente.")
            except ValueError:
                print("Entrada inválida. Digite um número ou 'q' para sair.")

class MCTSPlayer:
    def __init__(self, iterations: int = 1000):
        self.iterations = iterations
    
    def get_move(self, board: Board) -> int:
        """Obtém movimento da IA usando MCTS"""
        print("IA está pensando...")
        mcts = MCTS(board, iterations=self.iterations)
        return mcts.search()
    
class aStarPlayer:
    def __init__(self, iterations: int = 1000):
        self.iterations = iterations
    
    def get_move(self, board: Board) -> int:
        """Obtém movimento da IA usando MCTS"""
        print("IA está pensando...")
        s_star = a_Star(board, iterations=self.iterations)
        return a_Star.search()