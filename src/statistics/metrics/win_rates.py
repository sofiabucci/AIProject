import numpy as np
from datetime import datetime
from storage import save_metrics, load_metrics

def record_game_result(ai_type: str, opponent_type: str, result: str, phase_data: dict = None):
    """Registra o resultado de um jogo e opcionalmente dados por fase"""
    timestamp = datetime.now().isoformat()
    data = {
        'ai_type': ai_type,
        'opponent': opponent_type,
        'result': result,
        'timestamp': timestamp
    }
    
    if phase_data:
        data.update(phase_data)
    
    save_metrics('win_rates', data)

def calculate_win_rates(ai_type: str, opponent_type: str = 'random', n_games: int = 100):
    """Calcula estatísticas de vitória com base em dados históricos"""
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