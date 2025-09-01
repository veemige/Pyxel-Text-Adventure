import pyxel as px
import random

# Constantes de layout
WIDTH, HEIGHT = 320, 240
SPLIT_Y = HEIGHT // 2  # metade da tela
TEXT_COLOR = 11        # indice 11 (vamos ajustar para verde)
BG_COLOR = 0

# Tamanho da fonte padrao do Pyxel (4x6 px por caractere)
CHAR_W, CHAR_H = 4, 6

# Fonte bitmap estendida (acentos) - coordenadas (u,v) na imagem 0 do assets.pyxres
# Cada glifo deve ter tamanho 4x6 pixels.
EXT_FONT_MAP = {
    "á": (0, 0),  "é": (4, 0),  "í": (8, 0),  "ó": (12, 0), "ú": (16, 0),
    "â": (20, 0), "ê": (24, 0), "ô": (28, 0),
    "ã": (32, 0), "õ": (36, 0), "à": (40, 0), "ç": (44, 0),
    "Á": (0, 6),  "É": (4, 6),  "Í": (8, 6),  "Ó": (12, 6), "Ú": (16, 6),
    "Â": (20, 6), "Ê": (24, 6), "Ô": (28, 6),
    "Ã": (32, 6), "Õ": (36, 6), "À": (40, 6), "Ç": (44, 6),
}

class Character():
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
            "vida_max": 10,     # novo: vida máxima
            "forca": 1,
            "defesa": 1,
            "nivel": 1,
            "experiencia": 0,
            "pontos": 0,        # novo: pontos de habilidade
        }

        

    # novo: XP necessário para próximo nível (progressão linear simples)
    def xp_to_next(self) -> int:
        lvl = self.status["nivel"]
        return 10 + (lvl - 1) * 10

    # novo: ganhar XP e aplicar level ups em cascata
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

    # novo: alocar pontos em atributos
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
            # recupera a mesma quantidade na vida atual (sem passar do máximo)
            self.status["vida"] = min(self.status["vida"] + qty, self.status["vida_max"])
        else:
            self.status[target] += qty

        return True, f"{qty} ponto(s) atribuido(s) em {target}. Restantes: {self.status['pontos']}."

    def has_visited(self, room: str) -> bool:
        return room in self.visited_rooms

class App:
    def __init__(self):
        px.init(WIDTH, HEIGHT, title="TEXT ADVENTURE")

        # Ajuste de paleta (uma vez)
        px.colors[TEXT_COLOR] = 0x00FF00  # verde tipo monitor

        # Estado do console
        self.history = []
        self.input_buf = ""
        self.ext_map = EXT_FONT_MAP

        # Mapeamento de itens
        self.item_map = {
            "concha": {"tipo": "comum", "desc": "Uma concha do mar."},
            "galho": {"tipo": "arma", "desc": "Um galho seco.", "dano": 0.5},
            "tocha": {"tipo": "utensilio", "desc": "Uma tocha acesa.", "efeito": "ilumina o ambiente"},
            "adaga": {"tipo": "arma", "desc": "Uma adaga afiada.", "dano": 1.0}
        }

        # Mundo simples (salas, saidas, itens, cena)
        self.rooms = {
            "menu": {
                "desc": "Voce esta no menu principal.",
                "exits": {},
                "items": [],
                "scene": "menu",
                "region": "menu",
                "encounters_enabled": False,
            },
            "praia": {
                "desc": "Voce esta em uma praia silenciosa. O mar murmura ao sul. A luz da lua reflete nas ondas do mar a sua frente.",
                "exits": {"norte": "floresta", "leste": "caverna"},
                "items": ["concha"],
                "scene": "praia",
                "region": "praia",
                "encounters_enabled": True,
            },
            "floresta": {
                "desc": "Arvores densas bloqueiam parte da luz noturna. Ha um cheiro de terra molhada.",
                "exits": {"sul": "praia"},
                "items": ["galho"],
                "scene": "floresta",
                "region": "floresta",
                "encounters_enabled": True,
            },
            "caverna": {
                "desc": "Uma caverna escura e fria. Ecoa o som de gotas.",
                "exits": {"oeste": "praia", "entrada": "interior da caverna"},
                "items": ["tocha"],
                "scene": "caverna",
                "region": "caverna",
                "encounters_enabled": True,
            },
            "interior da caverna": {
                "desc": "Voce esta dentro de uma caverna escura. Ha um brilho fraco vindo de uma abertura ao norte.",
                "exits": {"norte": "planicie"},
                "items": [],
                "scene": "",
                "region": "caverna",
                "encounters_enabled": True,
            },
            "planicie": {
                "desc": "Voce chegou a uma planicie aberta com grama rala. O ceu estrelado se estende acima de voce.",
                "exits": {"sul": "interior da caverna", "oeste": "floresta", "norte": "leste da vila"},
                "items": [],
                "scene": "",
                "region": "planicie",
                "encounters_enabled": True,
            },
            "leste da vila": {
                "desc": "Voce chegou ao leste da vila. Casas simples se alinham ao longo da estrada de terra.",
                "exits": {"sul": "planicie", "oeste": "vila"},
                "items": [],
                "scene": "",
                "region": "vila",
                "encounters_enabled": True,
            },
        }
        self.room = "menu"
        self.char = Character()
        self.awaiting_name = True

        # novo: salas visitadas (para XP na primeira visita)
        self.visited_rooms = set()

        # Largura maxima de caracteres por linha no console
        self.max_cols = (WIDTH - 12) // CHAR_W  # margem de 6px de cada lado

        # Mensagem inicial
        self.say("Bem-vindo! Digite seu nome e pressione Enter. (Use 'ajuda' para dicas)")
        self.describe_room()

        # -------- Sistema de encontros --------
        # Probabilidade base de encontro aleatório ao entrar em uma sala habilitada
        self.encounter_chance = 0.25
        # Encontros cadastrados (data-driven)
        # Cada encontro pode restringir por 'rooms' e/ou 'regions', e por faixa de nível
        self.encounters = {
            "mercador_costeiro": {
                "type": "npc",
                "regions": ["praia", "planicie", "vila"],
                "min_level": 1,
                "weight": 1,
            },
            "caranguejo": {
                "type": "enemy",
                "regions": ["praia"],
                "min_level": 1,
                "max_level": 3,
                "weight": 3,
                "enemy": {"name": "Caranguejo", "base_hp": 4, "atk": 1},
            },
            "lobo": {
                "type": "enemy",
                "regions": ["floresta", "planicie"],
                "min_level": 2,
                "weight": 2,
                "enemy": {"name": "Lobo", "base_hp": 6, "atk": 2},
            },
            "morcego": {
                "type": "enemy",
                "regions": ["caverna"],
                "min_level": 1,
                "weight": 2,
                "enemy": {"name": "Morcego", "base_hp": 3, "atk": 1},
            },
        }
        # Encontros programados por sala (ex.: 1a vez que entra)
        self.scripted_by_room = {
            "interior da caverna": [
                {"id": "minero_intro", "type": "npc", "once": True, "min_level": 1, "handler": "script_miner"},
            ]
        }
        # Flags para encontros programados (evitar repetir 'once')
        self.encounter_flags = set()
        # --------------------------------------

        px.run(self.update, self.draw)

    # ---------------- Logica ----------------
    def update(self):
        self.handle_text_input()
        if self.char.status["vida"] <= 0:
            self.say("Você morreu!")
            self.say("Aperte [ENTER] para reiniciar.")
            if px.btnp(px.KEY_ENTER):
                px.reset()

    def handle_text_input(self):
        # Letras a-z
        for k, ch in self._alpha_keymap().items():
            if px.btnp(k):
                self.input_buf += ch

        # Numeros e espaco
        for k, ch in self._digit_space_keymap().items():
            if px.btnp(k):
                self.input_buf += ch

        # Backspace (com repeticao)
        if px.btnp(px.KEY_BACKSPACE, 10, 2) and self.input_buf:
            self.input_buf = self.input_buf[:-1]

        # Enter: processa comando
        if px.btnp(px.KEY_RETURN):
            cmd = self.input_buf.strip().lower()
            if cmd:
                self.say(f"> {cmd}")
                self.process_command(cmd)
            self.input_buf = ""

        if px.btnp(px.KEY_LSHIFT):
            self.char.gain_xp(10)

    def process_command(self, cmd: str):
        if self.room == "menu":
            # Primeiro, tratar entrada do nome
            if self.awaiting_name:
                if cmd in ("ajuda", "help", "?"):
                    self.say("Digite um nome e pressione Enter. Ou 'entrar' para manter 'Hero'.")
                    return
                if cmd == "entrar":
                    self.awaiting_name = False
                    # Entrar no jogo pela primeira vez
                    self.enter_room("praia")
                    return
                if cmd and cmd not in ("sair", "exit", "quit"):
                    self.char.name = cmd
                    self.awaiting_name = False
                    self.say(f"Nome definido: {self.char.name}. Digite 'entrar' para comecar.")
                    return
                # Se vazio, apenas ignore
                return

            # Menu sem estar aguardando nome
            if cmd in ("ajuda", "help", "?"):
                self.say("Menu: entrar | nome <novo> | ajuda")
                return
            if cmd.startswith("nome "):
                _, _, newname = cmd.partition(" ")
                if newname:
                    self.char.name = newname
                    self.say(f"Nome alterado para {self.char.name}.")
                else:
                    self.say("Use: nome <novo_nome>")
                return
            if cmd == "entrar":
                self.enter_room("praia")
                return
            self.say(f"Bem-vindo, {self.char.name}! Digite 'entrar' para comecar.")
            return

        # Ajuda
        if cmd in ("ajuda", "help", "?"):
            self.say(
                "Comandos: olhar | ir <norte/sul/leste/oeste> | pegar <item> | "
                "inventario | pontos | atribuir <vida|forca|defesa> <qtd> | limpar | status"
            )
            return
        # Olhar
        if cmd in ("olhar", "look", "l"):
            self.describe_room()
            return
        # Ir
        if cmd.startswith("ir ") or cmd.startswith("go "):
            _, _, rest = cmd.partition(" ")
            self.go(rest.strip())
            return
        # Pegar
        if cmd.startswith("pegar ") or cmd.startswith("take "):
            _, _, item = cmd.partition(" ")
            self.take(item.strip())
            return
        # Inventario
        if cmd in ("inventario", "inv", "i"):
            if self.char.inventory:
                self.say("Voce carrega: ")
                self.say("Utensilios: " + ", ".join(self.char.inventory["utensilios"]) if self.char.inventory["utensilios"] else "Utensilios: vazio")
                self.say("Armas: " + ", ".join(self.char.inventory["armas"]) if self.char.inventory["armas"] else "Armas: vazio")
                self.say("Armaduras: " + ", ".join(self.char.inventory["armaduras"]) if self.char.inventory["armaduras"] else "Armaduras: vazio")
                self.say("Comuns: " + ", ".join(self.char.inventory["comuns"]) if self.char.inventory["comuns"] else "Comuns: vazio")
            else:
                self.say("Voce nao carrega nada.")
            return

        if cmd in ("visitadas", "visited"):
            if self.char.visited_rooms:
                self.say("Salas visitadas: " + ", ".join(self.char.visited_rooms))
            else:
                self.say("Voce nao visitou nenhuma sala.")
            return
        # Debug/inspecao de encontros
        if cmd == "encontros":
            r = self.rooms[self.room]
            region = r.get("region")
            enabled = r.get("encounters_enabled", False)
            pool = self._eligible_encounters()
            ids = [eid for eid, _ in pool]
            self.say(f"Encontros aqui: {'ON' if enabled else 'OFF'} | Regiao: {region}")
            self.say("Elegiveis: " + (", ".join(ids) if ids else "nenhum"))
            self.say(f"Chance base: {self.encounter_chance:.2f}")
            return
        if cmd.startswith("forcar encontro "):
            _, _, eid = cmd.partition("forcar encontro ")
            eid = eid.strip()
            if eid:
                self.trigger_encounter(eid)
            else:
                self.say("Use: forcar encontro <id>")
            return
        if cmd.startswith("chance "):
            try:
                val = float(cmd.split()[1])
                self.encounter_chance = max(0.0, min(1.0, val))
                self.say(f"Chance de encontro ajustada para {self.encounter_chance:.2f}")
            except Exception:
                self.say("Use: chance <valor entre 0 e 1>")
            return
        # Limpar
        if cmd in ("limpar", "clear", "cls"):
            self.history.clear()
            return
        # Sair
        if cmd in ("sair", "exit", "quit"):
            self.say("Obrigado por jogar!")
            px.quit()
        # Status
        if cmd in ("status", "info"):
            self.say(f"Nome: {self.char.name}")
            self.say(f"Localizacao: {self.room}")
            lvl = self.char.status["nivel"]
            xp = self.char.status["experiencia"]
            to_next = self.char.xp_to_next()
            pts = self.char.status["pontos"]
            vida = self.char.status["vida"]
            vmax = self.char.status["vida_max"]
            forca = self.char.status["forca"]
            defesa = self.char.status["defesa"]
            self.say(f"Nível {lvl} | XP {xp}/{to_next} | Pontos {pts}")
            self.say(f"Atributos: Vida {vida}/{vmax}, Forca {forca}, Defesa {defesa}")
            return

        if cmd.startswith("usar ") or cmd.startswith("use "):
            _, _, item = cmd.partition(" ")
            self.use(item.strip())
            return

        self.say("Nao entendi. Digite 'ajuda'.")
    # Descrição dos ambientes
    def describe_room(self):
        r = self.rooms[self.room]
        self.say(r["desc"])
        if r["items"]:
            self.say("Ao redor: " + ", ".join(r["items"]))
        if r["exits"]:
            self.say("Saidas: " + ", ".join(sorted(r["exits"].keys())))
    # Mover-se entre os ambientes
    def go(self, direction: str):
        r = self.rooms[self.room]
        if direction in r["exits"]:
            self.enter_room(r["exits"][direction])
        else:
            self.say("Voce nao pode ir por ai.")
    # Pegar itens
    def take(self, item: str):
        if not item:
            self.say("Pegar o que?")
            return
        r = self.rooms[self.room]
        i = self.char.inventory
        if item in r["items"]:
            r["items"].remove(item)
            if self.item_map[item]["tipo"] == "utensilio":
                i["utensilios"].append(item)
            elif self.item_map[item]["tipo"] == "arma":
                i["armas"].append(item)
            elif self.item_map[item]["tipo"] == "armadura":
                i["armaduras"].append(item)
            else:
                i["comuns"].append(item)
            self.say(f"Voce pegou a {item}.")
            # novo: XP ao pegar item
            for m in self.char.gain_xp(3):
                self.say(m)
        else:
            self.say("Nao vejo isso aqui.")
    
    # Usar Itens
    def use(self, item: str):
        if not item:
            self.say("Usar o que?")
            return
        i = self.char.inventory
        if item in i["utensilios"]:
            self.say(f"Voce usou o {item}.")
            if item in self.item_map:
                effect = self.item_map[item].get("efeito")
                if effect:
                    self.say(f"O efeito do item {item} foi ativado: {effect}")
        else:
            self.say("Nao pode usar isso.")

    # ------- Entrada em sala (concede XP apenas na primeira vez) -------
    def enter_room(self, new_room: str):
        self.room = new_room
        if not self.char.has_visited(new_room):
            self.char.visited_rooms.add(new_room)
            for m in self.char.gain_xp(2):
                self.say(m)
        self.describe_room()
        # Encontros programados (por sala)
        self._maybe_trigger_scripted_encounter()
        # Encontro aleatório (se habilitado e sorte permitir)
        self._maybe_trigger_random_encounter()

    # ----------------- Encontros: núcleo -----------------
    def _eligible_encounters(self):
        room = self.room
        region = self.rooms[room].get("region")
        lvl = self.char.status["nivel"]
        pool = []
        for eid, e in self.encounters.items():
            rooms = e.get("rooms")
            regions = e.get("regions")
            if rooms and room not in rooms:
                continue
            if regions and region not in regions:
                continue
            if lvl < e.get("min_level", 1):
                continue
            if lvl > e.get("max_level", 999):
                continue
            pool.append((eid, e.get("weight", 1)))
        return pool
    
    def _maybe_trigger_random_encounter(self):
        r = self.rooms[self.room]
        if not r.get("encounters_enabled", False):
            return
        if random.random() >= self.encounter_chance:
            return
        pool = self._eligible_encounters()
        if not pool:
            return
        eid = self._weighted_choice(pool)
        self.trigger_encounter(eid)
    
    def _maybe_trigger_scripted_encounter(self):
        room = self.room
        entries = self.scripted_by_room.get(room, [])
        if not entries:
            return
        lvl = self.char.status["nivel"]
        for e in entries:
            flag = f"script:{e['id']}"
            if e.get("once") and flag in self.encounter_flags:
                continue
            if lvl < e.get("min_level", 1):
                continue
            handler = e.get("handler")
            if handler and hasattr(self, handler):
                getattr(self, handler)()
            else:
                self.say(f"Um evento ocorre: {e['id']}")
            if e.get("once"):
                self.encounter_flags.add(flag)
    
    def trigger_encounter(self, encounter_id: str):
        e = self.encounters.get(encounter_id)
        if not e:
            self.say(f"Encontro '{encounter_id}' nao encontrado.")
            return
        if e["type"] == "npc":
            self._enc_npc(encounter_id, e)
        elif e["type"] == "enemy":
            self._enc_enemy(encounter_id, e)
        else:
            self.say(f"Encontro: {encounter_id}")
    
    def _enc_npc(self, eid, e):
        self.say("Um mercador aparece na estrada, oferecendo seus produtos.")
        self.say("Dica: voce pode implementar aqui um menu de compra ('comprar <item>').")
    
    def _enc_enemy(self, eid, e):
        data = e.get("enemy", {})
        name = data.get("name", "Inimigo")
        lvl = self.char.status["nivel"]
        self.say(f"Um {name} salta a sua frente! (area: {self.rooms[self.room].get('region')}, nivel {lvl})")
        self.say("Dica: daqui voce pode chamar um loop de combate.")
    
    def script_miner(self):
        self.say("Um mineiro cansado surge das sombras: 'Cuidado lá dentro.'")
    
    def _weighted_choice(self, items):
        total = sum(w for _, w in items)
        r = random.uniform(0, total)
        acc = 0
        for v, w in items:
            acc += w
            if r <= acc:
                return v
        return items[-1][0]

    # ---------------- Desenho ----------------
    def draw(self):
        px.cls(BG_COLOR)

        # Metade de cima: cenario simples
        self.draw_scene(0, 0, WIDTH, SPLIT_Y)

        # Separador
        px.rect(0, SPLIT_Y, WIDTH, 1, TEXT_COLOR)

        # Metade de baixo: console de texto
        self.draw_console(0, SPLIT_Y + 1, WIDTH, HEIGHT - (SPLIT_Y + 1))

    def draw_scene(self, x, y, w, h):
        # Ceu e "chao" base
        if self.awaiting_name and self.room == "menu" or self.room != "interior da caverna":
            px.rect(x, y, w, h, 1)              # azul escuro (ceu)
            px.rect(x, y + h - 30, w, 30, 3)    # verde (chao)

        # Desenhos por cena (rapidos)
        scene = self.rooms[self.room]["scene"]
        cx = x + w // 2
        base = y + h - 30

        if scene == "praia":
            px.circ(cx + 70, y + 20, 10, 13)
            px.rect(x, base - 20, w, 20, 12)   # mar (azul claro)
            px.rect(x, y + h - 30, w, 30, 15)   # areia (bege)
        elif scene == "floresta":
            for i in range(5):
                tx = x + 20 + i * 50
                px.rect(tx, base - 25, 6, 25, 4)   # tronco (marrom)
                px.tri(tx - 10, base - 10, tx + 3, base - 75, tx + 16, base - 10, 11)  # copa (verde claro)
        elif scene == "caverna":
            px.tri(cx - 70, base, cx - 40, base - 70, cx - 25, base, 0)
            px.tri(cx + 25, base, cx + 40, base - 70, cx + 70, base, 0)
            px.tri(cx - 35, base, cx, base - 90, cx + 35, base, 0)
            px.circ(cx, base - 20, 45, 0)
            px.rect(x, y + h - 30, w, 30, 3)
            px.rect(x, base, w, 30, 3)

    def draw_console(self, x, y, w, h):
        margin = 6
        # Quantas linhas cabem (reservando 1 para a linha de entrada)
        max_rows = (h - margin * 2) // CHAR_H
        visible_rows = max(1, max_rows - 1)

        # Linhas finais do historico
        lines = self.history[-visible_rows:]

        ty = y + margin
        for line in lines:
            self._draw_text_mixed(x + margin, ty, line, TEXT_COLOR)
            ty += CHAR_H

        # Prompt + cursor piscando
        cursor = "_" if (px.frame_count // 15) % 2 == 0 else " "
        prompt = f"> {self.input_buf}{cursor}"
        self._draw_text_mixed(x + margin, y + h - margin - CHAR_H, prompt, TEXT_COLOR)

    # ---------------- Utilitarios ----------------
    def say(self, text: str):
        # quebra de linha automatica por palavras
        for raw in text.split("\n"):
            self.history.extend(self._wrap(raw, self.max_cols))

    def _draw_text_mixed(self, x: int, y: int, s: str, col: int):
        """Desenha texto char a char. ASCII via px.text; acentos via atlas bitmap.
        Requer que assets.pyxres contenha os glifos mapeados em EXT_FONT_MAP.
        """
        cx = x
        for ch in s:
            if ch in self.ext_map:
                u, v = self.ext_map[ch]
                px.blt(cx, y, 0, u, v, CHAR_W, CHAR_H, 0)
                cx += CHAR_W
            else:
                px.text(cx, y, ch, col)
                cx += CHAR_W

    def _wrap(self, s: str, max_cols: int):
        if not s:
            return [""]
        out, line = [], ""
        for w in s.split():
            trial = (line + " " + w) if line else w
            if len(trial) <= max_cols:
                line = trial
            else:
                out.append(line)
                line = w
        if line:
            out.append(line)
        return out

    def _alpha_keymap(self):
        return {
            px.KEY_A:"a", px.KEY_B:"b", px.KEY_C:"c", px.KEY_D:"d",
            px.KEY_E:"e", px.KEY_F:"f", px.KEY_G:"g", px.KEY_H:"h",
            px.KEY_I:"i", px.KEY_J:"j", px.KEY_K:"k", px.KEY_L:"l",
            px.KEY_M:"m", px.KEY_N:"n", px.KEY_O:"o", px.KEY_P:"p",
            px.KEY_Q:"q", px.KEY_R:"r", px.KEY_S:"s", px.KEY_T:"t",
            px.KEY_U:"u", px.KEY_V:"v", px.KEY_W:"w", px.KEY_X:"x",
            px.KEY_Y:"y", px.KEY_Z:"z"
        }

    def _digit_space_keymap(self):
        return {
            px.KEY_SPACE:" ",
            px.KEY_0:"0", px.KEY_1:"1", px.KEY_2:"2", px.KEY_3:"3",
            px.KEY_4:"4", px.KEY_5:"5", px.KEY_6:"6", px.KEY_7:"7",
            px.KEY_8:"8", px.KEY_9:"9",
        }

App()