from game.board import Board
from game.player import HumanPlayer, AIPlayer
from ai.mcts import MCTSAgent
from ai.decision_tree import DecisionTreeAgent
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
        player2 = AIPlayer(2, MCTSAgent(iterations=1000))
    else:  # IA vs IA
        player1 = AIPlayer(1, MCTSAgent(iterations=1000))
        player2 = AIPlayer(2, DecisionTreeAgent())
    
    # Inicializa jogo
    board = Board()
    current_player = player1
    gui.draw_board(board)
    
    # Loop principal do jogo
    while not board.is_game_over:
        # Jogador humano
        if isinstance(current_player, HumanPlayer):
            col = gui.get_human_move(board)
        # Jogador IA
        else:
            pygame.time.delay(500)  # Delay para visualização
            col = current_player.get_move(board)
        
        if board.drop_piece(col):
            gui.draw_board(board)
            current_player = player2 if current_player == player1 else player1
    
    # Mostra resultado
    gui.show_game_over(board.winner)
    
    # Volta ao menu
    main()

if __name__ == "__main__":
    try:
        main()
    finally:
        pygame.quit()
        sys.exit()