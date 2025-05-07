class Player:
    def __init__(self, player_id):
        self.player_id = player_id

class HumanPlayer(Player):
    def get_move(self, board):
        while True:
            try:
                col = int(input(f"Player {self.player_id}, enter column (0-{board.cols-1}): "))
                if board.is_valid_move(col):
                    return col
                print("Invalid move. Try again.")
            except ValueError:
                print("Please enter a valid number.")

class AIPlayer(Player):
    def __init__(self, player_id, agent):
        super().__init__(player_id)
        self.agent = agent
    
    def get_move(self, board):
        return self.agent.get_best_move(board)