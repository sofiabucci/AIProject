import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import os
from pathlib import Path
import json
import pandas as pd
import time
import random
from game import rules as game
from game import constants as c
from game import board as Board
from statistics.storage import save_metrics, load_metrics
from statistics.metrics.critical_decisions import evaluate_decision_quality, get_decision_quality_stats
from statistics.metrics.response_time import measure_response_time, record_response_time
from statistics.metrics.win_rates import record_game_result, calculate_win_rates

class IA_Analysis:
    def __init__(self):
        self.results_dir = Path(__file__).parent / 'data' / 'results'
        self.plots_dir = Path(__file__).parent / 'data' / 'plots'
        self.create_dirs()
        
    def create_dirs(self):
        """Cria os diretórios necessários"""
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.plots_dir, exist_ok=True)
    
    def run_full_analysis(self, n_games=100):
        """Executa todos os testes e análises"""
        print("Iniciando análise completa das IAs...")
        
        # Testes contra random
        self.test_ia_vs_random(mcts.mcts, "MCTS", n_games)
        self.test_ia_vs_random(a_star.a_star, "A_STAR", n_games)
        self.test_ia_vs_random(decision_tree.DecisionTree().play, "DECISION_TREE", n_games)
        
        # Testes entre IAs
        self.test_ia_vs_ia(mcts.mcts, "MCTS", a_star.a_star, "A_STAR", n_games//2)
        self.test_ia_vs_ia(mcts.mcts, "MCTS", decision_tree.DecisionTree().play, "DECISION_TREE", n_games//2)
        self.test_ia_vs_ia(a_star.a_star, "A_STAR", decision_tree.DecisionTree().play, "DECISION_TREE", n_games//2)
        
        # Gera relatórios
        self.generate_reports()
        
        print("Análise completa concluída!")

    def test_ia_vs_random(self, ia_func, ia_name, n_games):
        """Executa uma série de jogos contra um oponente aleatório"""
        print(f"Executando {n_games} jogos {ia_name} vs Random...")
        
        for game_num in range(n_games):
            board = Board.create_board()
            game_over = False
            turn = random.randint(0, 1)  # Decide quem começa
            
            while not game_over:
                if turn == 0:  # Vez da IA
                    piece = c.PLAYER1_PIECE
                    start_time = time.perf_counter()
                    move = ia_func(board)
                    time_taken = time.perf_counter() - start_time
                    
                    # Registra métricas usando os módulos separados
                    self.record_critical_decision(ia_name, board, move, piece)
                    record_response_time(ia_name, time_taken)
                else:  # Vez do random
                    piece = c.PLAYER2_PIECE
                    move = random.choice(Board.available_moves(board))
                
                # Executa movimento
                Board.drop_piece(board, move, piece)
                
                # Determina fase do jogo
                phase = self.determine_game_phase(board)
                
                # Verifica vitória
                if Board.winning_move(board, piece):
                    if turn == 0:
                        record_game_result(ia_name, 'random', 'win', {'phase': phase})
                    else:
                        record_game_result(ia_name, 'random', 'loss', {'phase': phase})
                    game_over = True
                elif len(Board.available_moves(board)) == 0:
                    record_game_result(ia_name, 'random', 'draw', {'phase': phase})
                    game_over = True
                
                turn = 1 - turn  # Alterna jogador

    def test_ia_vs_ia(self, ia_func1, ia_name1, ia_func2, ia_name2, n_games):
        """Executa uma série de jogos entre duas IAs diferentes"""
        print(f"Executando {n_games} jogos {ia_name1} vs {ia_name2}...")
        
        for game_num in range(n_games):
            board = Board.create_board()
            game_over = False
            turn = 0  # Alterna entre 0 (primeira IA) e 1 (segunda IA)
            
            while not game_over:
                # Seleciona a IA atual
                if turn == 0:
                    current_ia = ia_name1
                    ia_func = ia_func1
                    piece = c.PLAYER1_PIECE
                else:
                    current_ia = ia_name2
                    ia_func = ia_func2
                    piece = c.PLAYER2_PIECE
                
                # Mede tempo de resposta
                start_time = time.perf_counter()
                move = ia_func(board)
                time_taken = time.perf_counter() - start_time
                
                # Registra métricas usando os módulos separados
                self.record_critical_decision(current_ia, board, move, piece)
                record_response_time(current_ia, time_taken)
                
                # Executa movimento
                Board.drop_piece(board, move, piece)
                
                # Determina fase do jogo
                phase = self.determine_game_phase(board)
                
                # Verifica vitória
                if Board.winning_move(board, piece):
                    winner = ia_name1 if turn == 0 else ia_name2
                    loser = ia_name2 if turn == 0 else ia_name1
                    record_game_result(winner, loser, 'win', {'phase': phase})
                    record_game_result(loser, winner, 'loss', {'phase': phase})
                    game_over = True
                elif len(Board.available_moves(board)) == 0:
                    record_game_result(ia_name1, ia_name2, 'draw', {'phase': phase})
                    record_game_result(ia_name2, ia_name1, 'draw', {'phase': phase})
                    game_over = True
                
                turn = 1 - turn  # Alterna jogador

    def determine_game_phase(self, board):
        """Determina a fase do jogo com base no número de peças colocadas"""
        total_pieces = np.sum(board != 0)
        total_positions = board.shape[0] * board.shape[1]
        
        if total_pieces < total_positions * 0.3:
            return 'early'
        elif total_pieces < total_positions * 0.7:
            return 'mid'
        else:
            return 'late'

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
        ia_list = ["MCTS", "A_STAR", "DECISION_TREE"]
        
        self.plot_win_rates(ia_list)
        self.plot_response_times(ia_list)
        self.plot_phase_efficacy(ia_list)
        self.plot_decision_quality(ia_list)
    
    def plot_win_rates(self, ia_list):
        """Gráfico de taxas de vitória"""
        data = []
        for ia in ia_list:
            vs_random = calculate_win_rates(ia, 'random')
            if vs_random:
                data.append({
                    'IA': ia,
                    'Tipo': 'vs Random',
                    'Vitórias': vs_random['wins'],
                    'Derrotas': vs_random['losses'],
                    'Empates': vs_random['draws']
                })
            
            for opponent in ia_list:
                if opponent != ia:
                    vs_ia = calculate_win_rates(ia, opponent)
                    if vs_ia:
                        data.append({
                            'IA': ia,
                            'Tipo': f'vs {opponent}',
                            'Vitórias': vs_ia['wins'],
                            'Derrotas': vs_ia['losses'],
                            'Empates': vs_ia['draws']
                        })
        
        if not data:
            return
        
        # Processa dados para o gráfico
        df = pd.DataFrame(data)
        types = df['Tipo'].unique()
        
        # Configuração do gráfico
        plt.figure(figsize=(12, 8))
        bar_width = 0.25
        index = np.arange(len(ia_list))
        
        # Cria barras para cada tipo
        for i, t in enumerate(types):
            subset = df[df['Tipo'] == t]
            plt.bar(index + i*bar_width, subset['Vitórias'], bar_width, label=t)
        
        plt.xlabel('IA')
        plt.ylabel('Taxa de Vitórias')
        plt.title('Desempenho das IAs contra diferentes oponentes')
        plt.xticks(index + bar_width, ia_list)
        plt.legend()
        plt.tight_layout()
        plt.savefig(self.plots_dir / 'win_rates.png')
        plt.close()
    
    def plot_response_times(self, ia_list):
        """Gráfico de tempos de resposta médios"""
        plt.figure(figsize=(10, 6))
        
        for ia in ia_list:
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
    
    def plot_phase_efficacy(self, ia_list):
        """Gráfico de eficácia por fase do jogo"""
        plt.figure(figsize=(12, 8))
        
        phases = ['early', 'mid', 'late']
        width = 0.2
        index = np.arange(len(phases))
        
        for i, ia in enumerate(ia_list):
            win_rates = []
            for phase in phases:
                data = load_metrics('win_rates')
                filtered = [d for d in data 
                          if d['ai_type'] == ia 
                          and 'phase' in d 
                          and d['phase'] == phase]
                
                if not filtered:
                    win_rates.append(0)
                    continue
                    
                wins = sum(1 for d in filtered if d['result'] == 'win')
                win_rates.append(wins / len(filtered))
            
            plt.bar(index + i*width, win_rates, width, label=ia)
        
        plt.xlabel('Fase do Jogo')
        plt.ylabel('Taxa de Vitórias')
        plt.title('Eficácia das IAs por Fase do Jogo')
        plt.xticks(index + width, phases)
        plt.legend()
        plt.savefig(self.plots_dir / 'phase_efficacy.png')
        plt.close()
    
    def plot_decision_quality(self, ia_list):
        """Gráfico de qualidade das decisões"""
        plt.figure(figsize=(12, 8))
        
        for ia in ia_list:
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
    analyzer.run_full_analysis(n_games=50)