from game.board import Board
from game.player import HumanPlayer, AIPlayer
from ai.mcts import MCTSAgent
from ai.a_star import AStarAgent
from game.interface import GraphicalInterface
import pygame
import sys


def main():
    # Inicializa interface
    gui = GraphicalInterface()
    
    # Seleciona modo de jogo
    game_mode = gui.get_game_mode()
    
    # Configura jogadores
    if game_mode == 1:  # Humano vs Humano
        player1 = HumanPlayer(1)
        player2 = HumanPlayer(2)
       
    elif game_mode == 2:  # Humano vs IA
        player1 = HumanPlayer(1)
        player2 = AIPlayer(2, MCTSAgent(iterations=5000))
        
    else:  # IA vs IA
        player1 = AIPlayer(1, MCTSAgent(iterations=5000))
        player2 = AIPlayer(2, AStarAgent(max_depth=5))
    
    # Inicializa jogo
    board = Board()
    current_player = player1
    gui.draw_board(board)
    
    if game_mode==1:
         while not board.is_game_over:
            if isinstance(current_player, HumanPlayer):
                col = gui.get_human_move(board)
            else:
                pygame.time.delay(500)  # Delay para visualização
                col = current_player.get_move(board)
            if board.drop_piece(col):
                gui.draw_board(board)
                current_player = player2 if current_player == player1 else player1

    elif game_mode==2:
         while not board.is_game_over:
            if isinstance(current_player, HumanPlayer):
                col = gui.get_human_move(board)
            else:
                pygame.time.delay(500)  # Delay para visualização
                col = current_player.get_move(board)
            if board.drop_piece(col):
                gui.draw_board(board)
                current_player = player2 if current_player == player1 else player1

    else:
         while not board.is_game_over:
            if isinstance(current_player, HumanPlayer):
                col = gui.get_human_move(board)
            else:
                pygame.time.delay(500)  # Delay para visualização
                col = current_player.get_move(board)
            if board.drop_piece(col):
                pygame.time.delay(500)
                gui.draw_board(board)

     

    # Mostra resultado
    gui.show_game_over(board.winner)
    
    # Aguarda antes de fechar a interface
    gui.wait_for_exit()

if __name__ == "__main__":
    try:
        main()
    finally:
        pygame.quit()
        sys.exit()