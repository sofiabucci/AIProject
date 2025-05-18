import numpy as np
import json
import os
import time
import random
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from datetime import datetime
from game import rules as game
from game import constants as c
from game import board as Board
from ai import mcts, decision_tree, heuristic as h

# ==================== STORAGE MODULE ====================
DATA_DIR = Path(__file__).parent / 'data' / 'results'
PLOTS_DIR = Path(__file__).parent / 'data' / 'plots'

def save_metrics(metric_name: str, data: dict):
    """Salva métricas em arquivo JSON"""
    os.makedirs(DATA_DIR, exist_ok=True)
    file_path = DATA_DIR / f'{metric_name}.json'
    
    existing_data = []
    if file_path.exists():
        with open(file_path, 'r') as f:
            existing_data = json.load(f)
    
    existing_data.append(data)
    
    with open(file_path, 'w') as f:
        json.dump(existing_data, f, indent=2)

def load_metrics(metric_name: str):
    """Carrega métricas de arquivo JSON"""
    file_path = DATA_DIR / f'{metric_name}.json'
    
    if not file_path.exists():
        return []
    
    with open(file_path, 'r') as f:
        return json.load(f)

# ==================== CRITICAL DECISIONS MODULE ====================
def evaluate_decision_quality(board: np.ndarray, move: int, piece: int) -> dict:
    """Avalia a qualidade de uma decisão com base em heurísticas"""
    new_board = game.simulate_move(board, piece, move)
    
    if game.winning_move(new_board, piece):
        return {'decision_type': 'winning', 'quality': 1.0}
    
    opponent_piece = c.PLAYER2_PIECE if piece == c.PLAYER1_PIECE else c.PLAYER1_PIECE
    for col in game.available_moves(board):
        opponent_board = game.simulate_move(board, opponent_piece, col)
        if game.winning_move(opponent_board, opponent_piece):
            if col == move:
                return {'decision_type': 'blocking', 'quality': 0.9}
    
    original_score = h.calculate_board_score(board, piece, opponent_piece)
    new_score = h.calculate_board_score(new_board, piece, opponent_piece)
    improvement = (new_score - original_score) / max(1, abs(original_score))
    
    if improvement > 0.5:
        return {'decision_type': 'strong_improvement', 'quality': improvement}
    elif improvement > 0:
        return {'decision_type': 'improvement', 'quality': improvement}
    else:
        return {'decision_type': 'neutral', 'quality': improvement}

def get_decision_quality_stats(ai_type: str):
    """Retorna estatísticas sobre a qualidade das decisões"""
    data = load_metrics('critical_decisions')
    filtered = [d for d in data if d['ai_type'] == ai_type]
    
    if not filtered:
        return None
    
    decision_types = {}
    quality_scores = [d['quality'] for d in filtered]
    
    for d in filtered:
        if d['decision_type'] not in decision_types:
            decision_types[d['decision_type']] = 0
        decision_types[d['decision_type']] += 1
    
    return {
        'total_decisions': len(filtered),
        'decision_types': decision_types,
        'average_quality': sum(quality_scores) / len(quality_scores),
        'quality_distribution': {
            'excellent': sum(1 for q in quality_scores if q >= 0.8) / len(quality_scores),
            'good': sum(1 for q in quality_scores if 0.5 <= q < 0.8) / len(quality_scores),
            'neutral': sum(1 for q in quality_scores if -0.5 <= q < 0.5) / len(quality_scores),
            'poor': sum(1 for q in quality_scores if q < -0.5) / len(quality_scores)
        }
    }

# ==================== RESPONSE TIME MODULE ====================
def measure_response_time(ai_func, board: np.ndarray) -> float:
    """Mede o tempo de resposta de uma função IA"""
    start_time = time.perf_counter()
    _ = ai_func(board)
    return time.perf_counter() - start_time

def record_response_time(ai_type: str, time_taken: float, game_phase: str = None):
    """Registra o tempo de resposta de uma IA"""
    data = {
        'ai_type': ai_type,
        'time_taken': time_taken,
        'timestamp': datetime.now().isoformat()
    }
    
    if game_phase:
        data['game_phase'] = game_phase
    
    save_metrics('response_times', data)

# ==================== WIN RATES MODULE ====================
def record_game_result(ai_type: str, opponent_type: str, result: str, phase_data: dict = None):
    """Registra o resultado de um jogo"""
    data = {
        'ai_type': ai_type,
        'opponent': opponent_type,
        'result': result,
        'timestamp': datetime.now().isoformat()
    }
    
    if phase_data:
        data.update(phase_data)
    
    save_metrics('win_rates', data)

def calculate_win_rates(ai_type: str, opponent_type: str = 'random', n_games: int = 100):
    """Calcula estatísticas de vitória"""
    data = load_metrics('win_rates')
    filtered = [d for d in data if d['ai_type'] == ai_type and d['opponent'] == opponent_type]
    
    if not filtered:
        return None
    
    results = [d['result'] for d in filtered[-n_games:]]
    
    return {
        'wins': results.count('win') / len(results),
        'losses': results.count('loss') / len(results),
        'draws': results.count('draw') / len(results),
        'total_games': len(results)
    }

# ==================== MAIN ANALYSIS CLASS ====================
class IA_Analysis:
    def __init__(self):
        self.results_dir = DATA_DIR
        self.plots_dir = PLOTS_DIR
        self.create_dirs()
        
        self.ai_functions = {
            'RANDOM': lambda board: random.choice(game.available_moves(board)),
            'MCTS': mcts.mcts,
            'DECISION_TREE': decision_tree.DecisionTree('connect4').play
        }
    
    def create_dirs(self):
        """Cria os diretórios necessários"""
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.plots_dir, exist_ok=True)
    
    def run_full_analysis(self, n_games=100):
        """Executa todos os testes e análises"""
        print("Iniciando análise completa das IAs...")
        
        ia_combinations = [
            ('MCTS', 'RANDOM'),
            ('DECISION_TREE', 'RANDOM'),
            ('MCTS', 'DECISION_TREE'),
        ]
        
        for ia1, ia2 in ia_combinations:
            self.run_test(ia1, ia2, n_games//2)
        
        self.generate_reports()
        print("Análise completa concluída!")

    def run_test(self, ia_type1, ia_type2, n_games):
        """Testa qualquer combinação de IAs"""
        print(f"Executando {n_games} jogos {ia_type1} vs {ia_type2}...")
        
        for _ in range(n_games):
            board = Board.create_board()
            game_over = False
            turn = 0
            
            while not game_over:
                current_ia = ia_type1 if turn == 0 else ia_type2
                piece = c.PLAYER1_PIECE if turn == 0 else c.PLAYER2_PIECE
                
                start_time = time.perf_counter()
                move = self.ai_functions[current_ia](board)
                time_taken = time.perf_counter() - start_time
                
                if current_ia != 'RANDOM':
                    self.record_critical_decision(current_ia, board, move, piece)
                    record_response_time(current_ia, time_taken)
                
                Board.drop_piece(board, move, piece)
                
                if Board.winning_move(board, piece):
                    winner = ia_type1 if turn == 0 else ia_type2
                    loser = ia_type2 if turn == 0 else ia_type1
                    record_game_result(winner, loser, 'win')
                    record_game_result(loser, winner, 'loss')
                    game_over = True
                elif len(game.available_moves(board)) == 0:
                    record_game_result(ia_type1, ia_type2, 'draw')
                    record_game_result(ia_type2, ia_type1, 'draw')
                    game_over = True
                
                turn = 1 - turn

    def record_critical_decision(self, ai_type, board, move, piece):
        """Registra decisões críticas"""
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
        """Gera relatórios e gráficos"""
        print("Gerando relatórios...")
        ia_list = ["MCTS", "DECISION_TREE", "RANDOM"]
        
        self.plot_win_rates(ia_list)
        self.plot_response_times(ia_list)
        self.plot_decision_quality(ia_list)
    
    def plot_win_rates(self, ia_list):
        """Gráfico de taxas de vitória"""
        data = []
        for ia in ia_list:
            if ia == 'RANDOM':
                continue
                
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
        
        plt.figure(figsize=(14, 8))
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
        """Gráfico de tempos de resposta"""
        plt.figure(figsize=(10, 6))
        
        for ia in ia_list:
            if ia == 'RANDOM':
                continue
                
            data = load_metrics('response_times')
            filtered = [d['time_taken'] for d in data if d['ai_type'] == ia]
            
            if not filtered:
                continue
                
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
        """Gráfico de qualidade das decisões"""
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

# ==================== MAIN EXECUTION ====================
if __name__ == "__main__":
    analyzer = IA_Analysis()
    analyzer.run_full_analysis(n_games=50)