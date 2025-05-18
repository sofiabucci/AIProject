import numpy as np
from datetime import datetime
from storage import save_metrics, load_metrics
from game import rules as game
from game import constants as c
from ai import heuristic as h

def evaluate_decision_quality(board: np.ndarray, move: int, piece: int) -> dict:
    """Avalia a qualidade de uma decisão com base em heurísticas"""
    # Simula o movimento
    new_board = game.simulate_move(board, piece, move)
    
    # Verifica se é vitória imediata
    if game.winning_move(new_board, piece):
        return {'decision_type': 'winning', 'quality': 1.0}
    
    # Verifica se bloqueia vitória do oponente
    opponent_piece = c.PLAYER2_PIECE if piece == c.PLAYER1_PIECE else c.PLAYER1_PIECE
    for col in game.available_moves(board):
        opponent_board = game.simulate_move(board, opponent_piece, col)
        if game.winning_move(opponent_board, opponent_piece):
            if col == move:
                return {'decision_type': 'blocking', 'quality': 0.9}
    
    # Calcula melhoria heurística
    original_score = h.calculate_board_score(board, piece, opponent_piece)
    new_score = h.calculate_board_score(new_board, piece, opponent_piece)
    improvement = (new_score - original_score) / max(1, abs(original_score))
    
    # Classifica a decisão
    if improvement > 0.5:
        return {'decision_type': 'strong_improvement', 'quality': improvement}
    elif improvement > 0:
        return {'decision_type': 'improvement', 'quality': improvement}
    else:
        return {'decision_type': 'neutral', 'quality': improvement}

def record_critical_decision(ai_type: str, board: np.ndarray, move: int, piece: int):
    """Registra uma decisão crítica para análise posterior"""
    evaluation = evaluate_decision_quality(board, move, piece)
    data = {
        'ai_type': ai_type,
        'move': move,
        'piece': piece,
        'timestamp': datetime.now().isoformat(),
        **evaluation
    }
    save_metrics('critical_decisions', data)

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