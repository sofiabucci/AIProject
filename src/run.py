import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import os
from pathlib import Path
import pandas as pd
import time
import random
from game import rules as game
from game import constants as c
from game import board as Board
from storage import save_metrics, load_metrics
from critical_decisions import evaluate_decision_quality, get_decision_quality_stats
from response_time import measure_response_time, record_response_time
from win_rates import record_game_result, calculate_win_rates

class IA_Analysis:
    def __init__(self):
        self.results_dir = Path(__file__).parent / 'data' / 'results'
        self.plots_dir = Path(__file__).parent / 'data' / 'plots'
        self.create_dirs()
        
        # Dicionário de funções de IA (incluindo random como uma IA)
        self.ai_functions = {
            'RANDOM': lambda board: random.choice(Board.available_moves(board)),
            'MCTS': None,  # Será definido no main
            'A_STAR': None,
            'DECISION_TREE': None
        }
        
    def create_dirs(self):
        """Cria os diretórios necessários"""
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.plots_dir, exist_ok=True)
    
    def run_full_analysis(self, n_games=100):
        """Executa todos os testes e análises"""
        print("Iniciando análise completa das IAs...")
        
        # Todas as combinações de IA (incluindo random)
        ia_combinations = [
            ('MCTS', 'RANDOM'),
            ('A_STAR', 'RANDOM'),
            ('DECISION_TREE', 'RANDOM'),
            ('MCTS', 'A_STAR'),
            ('MCTS', 'DECISION_TREE'),
            ('A_STAR', 'DECISION_TREE')
        ]
        
        # Executa todos os testes
        for ia1, ia2 in ia_combinations:
            self.run_test(ia1, ia2, n_games//2)
        
        # Gera relatórios
        self.generate_reports()
        
        print("Análise completa concluída!")

    def run_test(self, ia_type1, ia_type2, n_games):
        """Método unificado para testar qualquer combinação de IAs"""
        print(f"Executando {n_games} jogos {ia_type1} vs {ia_type2}...")
        
        for _ in range(n_games):
            board = Board.create_board()
            game_over = False
            turn = 0  # Alterna entre 0 (primeira IA) e 1 (segunda IA)
            
            while not game_over:
                # Seleciona a IA atual
                current_ia = ia_type1 if turn == 0 else ia_type2
                piece = c.PLAYER1_PIECE if turn == 0 else c.PLAYER2_PIECE
                
                # Mede tempo de resposta (exceto para random)
                start_time = time.perf_counter()
                move = self.ai_functions[current_ia](board)
                time_taken = time.perf_counter() - start_time
                
                # Registra métricas (exceto para random)
                if current_ia != 'RANDOM':
                    self.record_critical_decision(current_ia, board, move, piece)
                    record_response_time(current_ia, time_taken)
                
                # Executa movimento
                Board.drop_piece(board, move, piece)
                
                # Verifica vitória
                if Board.winning_move(board, piece):
                    winner = ia_type1 if turn == 0 else ia_type2
                    loser = ia_type2 if turn == 0 else ia_type1
                    record_game_result(winner, loser, 'win')
                    record_game_result(loser, winner, 'loss')
                    game_over = True
                elif len(Board.available_moves(board)) == 0:
                    record_game_result(ia_type1, ia_type2, 'draw')
                    record_game_result(ia_type2, ia_type1, 'draw')
                    game_over = True
                
                turn = 1 - turn  # Alterna jogador

    def record_critical_decision(self, ai_type, board, move, piece):
        """Wrapper para a função do módulo critical_decisions"""
        evaluation = evaluate_decision_quality(board, move, piece)
        data = {
            'ai_type': ai_type,
            'move': move,
            'piece': piece,
            'timestamp': datetime.now().isoformat(),
            **evaluation
        }
        save_metrics('critical_decisions', data)

    def generate_reports(self):
        """Gera relatórios e gráficos com os resultados"""
        print("Gerando relatórios...")
        ia_list = ["MCTS", "A_STAR", "DECISION_TREE", "RANDOM"]
        
        self.plot_win_rates(ia_list)
        self.plot_response_times(ia_list)
        self.plot_decision_quality(ia_list)
    
    def plot_win_rates(self, ia_list):
        """Gráfico de taxas de vitória"""
        data = []
        for ia in ia_list:
            if ia == 'RANDOM':
                continue  # Não calculamos vitórias do random como IA principal
                
            for opponent in ia_list:
                if opponent != ia:
                    win_rates = calculate_win_rates(ia, opponent)
                    if win_rates:
                        data.append({
                            'IA': ia,
                            'Oponente': opponent,
                            'Vitórias': win_rates['wins'],
                            'Derrotas': win_rates['losses'],
                            'Empates': win_rates['draws']
                        })
        
        if not data:
            return
        
        # Configuração do gráfico
        plt.figure(figsize=(14, 8))
        
        # Gráfico de barras agrupadas
        df = pd.DataFrame(data)
        n_ias = len(df['IA'].unique())
        bar_width = 0.25
        index = np.arange(n_ias)
        
        for i, (opponent, group) in enumerate(df.groupby('Oponente')):
            plt.bar(index + i*bar_width, group['Vitórias'], bar_width, label=f'vs {opponent}')
        
        plt.xlabel('IA')
        plt.ylabel('Taxa de Vitórias')
        plt.title('Desempenho das IAs contra diferentes oponentes')
        plt.xticks(index + bar_width, df['IA'].unique())
        plt.legend()
        plt.tight_layout()
        plt.savefig(self.plots_dir / 'win_rates.png')
        plt.close()
    
    def plot_response_times(self, ia_list):
        """Gráfico de tempos de resposta médios (exclui RANDOM)"""
        plt.figure(figsize=(10, 6))
        
        for ia in ia_list:
            if ia == 'RANDOM':
                continue
                
            data = load_metrics('response_times')
            filtered = [d['time_taken'] for d in data if d['ai_type'] == ia]
            
            if not filtered:
                continue
                
            # Calcula média e desvio padrão
            avg_time = np.mean(filtered)
            std_dev = np.std(filtered)
            
            plt.bar(ia, avg_time, yerr=std_dev, capsize=5, label=ia)
        
        plt.xlabel('IA')
        plt.ylabel('Tempo médio (segundos)')
        plt.title('Tempo de resposta das IAs')
        plt.legend()
        plt.savefig(self.plots_dir / 'response_times.png')
        plt.close()
    
    def plot_decision_quality(self, ia_list):
        """Gráfico de qualidade das decisões (exclui RANDOM)"""
        plt.figure(figsize=(12, 8))
        
        for ia in ia_list:
            if ia == 'RANDOM':
                continue
                
            stats = get_decision_quality_stats(ia)
            if not stats:
                continue
                
            qualities = [
                stats['quality_distribution']['excellent'],
                stats['quality_distribution']['good'],
                stats['quality_distribution']['neutral'],
                stats['quality_distribution']['poor']
            ]
            
            labels = ['Excelente', 'Boa', 'Neutra', 'Ruim']
            plt.plot(labels, qualities, 'o-', label=ia)
        
        plt.xlabel('Qualidade da Decisão')
        plt.ylabel('Proporção')
        plt.title('Distribuição da Qualidade das Decisões')
        plt.legend()
        plt.savefig(self.plots_dir / 'decision_quality.png')
        plt.close()

if __name__ == "__main__":
    # Importa as IAs aqui para evitar circular imports
    from ai import mcts, a_star, decision_tree
    
    analyzer = IA_Analysis()
    
    # Configura as funções de IA
    analyzer.ai_functions['MCTS'] = mcts.mcts
    analyzer.ai_functions['A_STAR'] = a_star.a_star
    analyzer.ai_functions['DECISION_TREE'] = decision_tree.DecisionTree().play
    
    analyzer.run_full_analysis(n_games=50)