class Character:
    def __init__(self):
        self.name = "Hero"
        self.visited_rooms = set()
        self.inventory = {
            "utensilios": [],
            "armas": [],
            "armaduras": [],
            "comuns": []
        }
        self.status = {
            "vida": 10,
            "vida_max": 10,
            "forca": 1,
            "defesa": 1,
            "nivel": 1,
            "experiencia": 0,
            "pontos": 0,
            "energia": 5,
            "energia_max": 5,
            "agilidade": 1,
        }

    def xp_to_next(self) -> int:
        lvl = self.status["nivel"]
        return 10 + (lvl - 1) * 10

    def gain_xp(self, amount: int):
        msgs = []
        if amount <= 0:
            return msgs
        self.status["experiencia"] += amount
        msgs.append(f"+{amount} XP.")
        while self.status["experiencia"] >= self.xp_to_next():
            need = self.xp_to_next()
            self.status["experiencia"] -= need
            self.status["nivel"] += 1
            self.status["pontos"] += 2
            self.status["vida_max"] += 2
            self.status["vida"] = self.status["vida_max"]
            msgs.append(f"Subiu para o nivel {self.status['nivel']}! +2 pontos. Vida +2 e restaurada.")
        return msgs

    def allocate_points(self, attr: str, qty: int):
        attr = attr.lower()
        if attr in ("vida", "hp"):
            target = "vida"
        elif attr == "forca":
            target = "forca"
        elif attr == "defesa":
            target = "defesa"
        else:
            return False, "Atributo invalido. Use vida, forca ou defesa."

        if qty <= 0:
            return False, "Quantidade deve ser positiva."

        pts = self.status["pontos"]
        if qty > pts:
            return False, f"Você so tem {pts} ponto(s)."

        self.status["pontos"] -= qty
        if target == "vida":
            self.status["vida_max"] += qty
            self.status["vida"] = min(self.status["vida"] + qty, self.status["vida_max"])
        else:
            self.status[target] += qty

        return True, f"{qty} ponto(s) atribuido(s) em {target}. Restantes: {self.status['pontos']}."

    def has_visited(self, room: str) -> bool:
        return room in self.visited_rooms
