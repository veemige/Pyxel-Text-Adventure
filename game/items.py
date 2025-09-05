import json
import os

def load_item_data():
    """Carrega definicoes e posicoes de itens a partir de um arquivo JSON."""
    path = os.path.join(os.path.dirname(__file__), 'item_data.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # JSON converte tuplas em listas, entao convertemos de volta se necessario.
            positions = data.get("positions", {})
            for room, items in positions.items():
                for item, pos in items.items():
                    positions[room][item] = tuple(pos)
            return data.get("definitions", {}), positions
    except FileNotFoundError:
        print(f"Erro: Arquivo de itens '{path}' nao encontrado.")
        return {}, {}
    except json.JSONDecodeError:
        print(f"Erro: Falha ao decodificar o JSON em '{path}'.")
        return {}, {}

ITEMS, ITEM_POSITIONS = load_item_data()
