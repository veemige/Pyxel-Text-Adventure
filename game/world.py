import json
import os

def load_world_data():
    """Carrega os dados do mundo a partir de um arquivo JSON."""
    path = os.path.join(os.path.dirname(__file__), 'world_data.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Erro: Arquivo de mundo '{path}' nao encontrado.")
        return {}
    except json.JSONDecodeError:
        print(f"Erro: Falha ao decodificar o JSON em '{path}'.")
        return {}

WORLD = load_world_data()
