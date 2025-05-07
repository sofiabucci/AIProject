from game.interface import GameInterface
from game.board import Board
from game.player import HumanPlayer, AIPlayer
from mcts import MCTSAgent
from decision_tree import DecisionTreeAgent
import time

class GameController:
    def __init__(self):
        self.board = Board()
        self.interface = GameInterface()
        self.mcts_agent = MCTSAgent(iterations=1000)
        self.dt_agent = DecisionTreeAgent(model_path='models/connect4_model.pkl')
        self.player1 = None
        self.player2 = None
    
    def setup_players(self, mode):
        if mode == 1:  # Human vs Human
            self.player1 = HumanPlayer(1)
            self.player2 = HumanPlayer(2)
        elif mode == 2:  # Human vs AI (MCTS)
            self.player1 = HumanPlayer(1)
            self.player2 = AIPlayer(2, self.mcts_agent)
        elif mode == 3:  # AI (MCTS) vs AI (Decision Tree)
            self.player1 = AIPlayer(1, self.mcts_agent)
            self.player2 = AIPlayer(2, self.dt_agent)
    
    def run(self):
        print("Select game mode:")
        print("1. Human vs Human")
        print("2. Human vs Computer (MCTS)")
        print("3. Computer (MCTS) vs Computer (Decision Tree)")
        mode = int(input("Enter mode (1-3): "))
        
        self.setup_players(mode)
        current_player = self.player1
        
        while True:
            self.interface.display_board(self.board)
            
            if isinstance(current_player, HumanPlayer):
                col = current_player.get_move(self.board)
            else:
                print(f"AI ({'MCTS' if current_player.agent == self.mcts_agent else 'DT'}) is thinking...")
                start_time = time.time()
                col = current_player.get_move(self.board)
                print(f"Move took {time.time() - start_time:.2f} seconds")
            
            if self.board.make_move(col, current_player.player_id):
                if self.board.check_winner(current_player.player_id):
                    self.interface.display_board(self.board)
                    print(f"Player {current_player.player_id} wins!")
                    break
                elif self.board.is_full():
                    self.interface.display_board(self.board)
                    print("It's a draw!")
                    break
                
                current_player = self.player2 if current_player == self.player1 else self.player1

if __name__ == "__main__":
    game = GameController()
    game.run()