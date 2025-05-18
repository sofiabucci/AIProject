import json
import os
from pathlib import Path

DATA_DIR = Path(__file__).parent / 'results'

def save_metrics(metric_name: str, data: dict):
    """Salva métricas em arquivo JSON"""
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True)
    
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