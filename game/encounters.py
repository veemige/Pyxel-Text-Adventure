import random

ENCOUNTERS = {
    "mercador_costeiro": {
        "type": "npc",
        "regions": ["praia", "planicie", "vila"],
        "min_level": 1,
        "weight": 1,
        # Inventário da loja (item: preco). Se ausente, cai no item_map.preco
        "shop": {
            "pocao de vida": 5,
            "adaga": 12,
            "armadura leve": 25,
         },
    },
    "caranguejo": {
        "type": "enemy",
        "regions": ["praia"],
        "min_level": 1,
        "max_level": 3,
        "weight": 3,
        "enemy": {"name": "Caranguejo", "base_hp": 4, "atk": 1},
        # Drop de ouro e itens
        "gold_drop": [1, 3],
        "drops": [
            {"item": "concha", "chance": 0.5, "min": 1, "max": 1},
        ],
    },
    "lobo": {
        "type": "enemy",
        "regions": ["floresta", "planicie"],
        "min_level": 2,
        "weight": 2,
        "enemy": {"name": "Lobo", "base_hp": 6, "atk": 2},
        "gold_drop": [2, 5],
        "drops": [
            {"item": "couro", "chance": 0.45, "min": 1, "max": 2},
        ],
    },
    "morcego": {
        "type": "enemy",
        "regions": ["caverna"],
        "min_level": 1,
        "weight": 2,
        "enemy": {"name": "Morcego", "base_hp": 3, "atk": 1},
        "gold_drop": [1, 2],
        "drops": [
            {"item": "dente", "chance": 0.35, "min": 1, "max": 1},
        ],
    },
    "thales": {
        "type": "enemy",
        "regions": ["caverna"],
        "min_level": 1,
        "weight": 0.01,
        "enemy": {"name": "thales", "base_hp": 100, "atk": 50},
        "gold_drop": [100, 200],
        "drops": [
            {"item": "camiseta do e-colab", "chance": 1.0, "min": 1, "max": 1}
        ],
    },
    "O PESCADOR": {
        "type": "enemy",
        "regions": ["rio"],
        "min_level": 1,
        "weight": 5,
        "enemy": {"name": "O PESCADOR", "base_hp": 12, "atk": 5},
        "gold_drop": [2, 4],
        "drops": [
            {"item": "vara de pesca", "chance": 1.0, "min": 1, "max": 1}
        ],
    },
}

SCRIPTED_BY_ROOM = {
    "interior da caverna": [
        {"id": "minero_intro", "type": "npc", "once": True, "min_level": 1, "handler": "script_miner"},
    ]
}


def weighted_choice(items):
    total = sum(w for _, w in items)
    r = random.uniform(0, total)
    acc = 0
    for v, w in items:
        acc += w
        if r <= acc:
            return v
    return items[-1][0]