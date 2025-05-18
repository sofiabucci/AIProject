import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import os
from pathlib import Path
import json
import pandas as pd
from ai import mcts, a_star, decision_tree
from game import rules as game
from game import constants as c
import random

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

    # [...] (mantenha os métodos test_ia_vs_random e test_ia_vs_ia iguais)

    def generate_reports(self):
        """Gera relatórios e gráficos com os resultados"""
        print("Gerando relatórios...")
        ia_list = ["MCTS", "A_STAR", "DECISION_TREE"]
        
        self.plot_win_rates(ia_list)
        self.plot_response_times(ia_list)
        self.plot_phase_efficacy(ia_list)
        self.plot_decision_quality(ia_list)
    
    def load_metric_data(self, metric_name):
        """Carrega dados de uma métrica específica"""
        file_path = self.results_dir / f'{metric_name}.json'
        if not file_path.exists():
            return []
        
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def plot_win_rates(self, ia_list):
        """Gráfico de taxas de vitória usando apenas matplotlib"""
        data = []
        for ia in ia_list:
            vs_random = self.calculate_win_rates(ia, 'random')
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
                    vs_ia = self.calculate_win_rates(ia, opponent)
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
    
    def calculate_win_rates(self, ai_type, opponent_type):
        """Calcula taxas de vitória com base nos dados salvos"""
        data = self.load_metric_data('win_rates')
        filtered = [d for d in data if d['ai_type'] == ai_type and d['opponent'] == opponent_type]
        
        if not filtered:
            return None
        
        results = [d['result'] for d in filtered]
        total = len(results)
        
        return {
            'wins': results.count('win') / total,
            'losses': results.count('loss') / total,
            'draws': results.count('draw') / total,
            'total_games': total
        }
    
    def plot_response_times(self, ia_list):
        """Gráfico de tempos de resposta médios"""
        plt.figure(figsize=(10, 6))
        
        for ia in ia_list:
            data = self.load_metric_data('response_times')
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
                data = self.load_metric_data('win_rates')
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
            stats = self.get_decision_quality_stats(ia)
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
    
    def get_decision_quality_stats(self, ai_type):
        """Obtém estatísticas de qualidade de decisões"""
        data = self.load_metric_data('critical_decisions')
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

if __name__ == "__main__":
    analyzer = IA_Analysis()
    analyzer.run_full_analysis(n_games=50)