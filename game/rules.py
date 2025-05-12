class GameRules:
    @staticmethod
    def is_terminal(board):
        """Check if the game is over"""
        return (board.check_winner(1) or 
                board.check_winner(2) or 
                board.is_full())
    
    @staticmethod
    def evaluate(board, player):
        """Evaluate board state for the given player"""
        if board.check_winner(player):
            return 100
        elif board.check_winner(3 - player):
            return -100
        return 0