import time
import numpy as np
from datetime import datetime
from results.storage import save_metrics

def measure_response_time(ai_func, board: 'np.ndarray') -> float:
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