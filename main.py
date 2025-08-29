import pyxel as px

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
        self.inventory = {
            "utensilios": [],
            "armas": [],
            "armaduras": [],
            "comuns": []
        }
        self.status = {
            "vida": 10,
            "forca": 1,
            "defesa": 1,
            "nível": 1,
            "experiencia": 0
        }

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
            "galho": {"tipo": "arma", "desc": "Um galho seco."},
            "tocha": {"tipo": "utensilio", "desc": "Uma tocha acesa.", "efeito": "ilumina o ambiente"},
        }

        # Mundo simples (salas, saidas, itens, cena)
        self.rooms = {
            "menu": {
                "desc": "Voce esta no menu principal.",
                "exits": {},
                "items": [],
                "scene": "menu",
            },
            "praia": {
                "desc": "Voce esta em uma praia silenciosa. O mar murmura ao sul. A luz da lua reflete nas ondas do mar a sua frente.",
                "exits": {"norte": "floresta", "leste": "caverna"},
                "items": ["concha"],
                "scene": "praia",
            },
            "floresta": {
                "desc": "Arvores densas bloqueiam parte da luz noturna. Ha um cheiro de terra molhada.",
                "exits": {"sul": "praia"},
                "items": ["galho"],
                "scene": "floresta",
            },
            "caverna": {
                "desc": "Uma caverna escura e fria. Ecoa o som de gotas.",
                "exits": {"oeste": "praia", "entrada": "interior da caverna"},
                "items": ["tocha"],
                "scene": "caverna",
            },
            "interior da caverna": {
                "desc": "Voce esta dentro de uma caverna escura. Ha um brilho fraco vindo de uma abertura ao norte.",
                "exits": {"norte": "planicie"},
                "items": [],
                "scene": "",
            },
            "planicie": {
                "desc": "Voce chegou a uma planicie aberta com grama rala. O ceu estrelado se estende acima de voce.",
                "exits": {"sul": "interior da caverna", "oeste": "floresta", "norte": "leste da vila"},
                "items": [],
                "scene": "",
            },
            "leste da vila": {
                "desc": "Voce chegou ao leste da vila. Casas simples se alinham ao longo da estrada de terra.",
                "exits": {"sul": "planicie", "oeste": "vila"},
                "items": [],
                "scene": "",
            },

        }
        self.room = "menu"
        self.char = Character()
        # Estado: aguardando o nome no menu
        self.awaiting_name = True

        # Largura maxima de caracteres por linha no console
        self.max_cols = (WIDTH - 12) // CHAR_W  # margem de 6px de cada lado

        # Mensagem inicial
        self.say("Bem-vindo! Digite seu nome e pressione Enter. (Use 'ajuda' para dicas)")
        self.describe_room()

        px.run(self.update, self.draw)

    # ---------------- Logica ----------------
    def update(self):
        self.handle_text_input()

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

    def process_command(self, cmd: str):
        if self.room == "menu":
            # Primeiro, tratar entrada do nome
            if self.awaiting_name:
                if cmd in ("ajuda", "help", "?"):
                    self.say("Digite um nome e pressione Enter. Ou 'entrar' para manter 'Hero'.")
                    return
                if cmd == "entrar":
                    self.awaiting_name = False
                    self.room = "praia"
                    self.describe_room()
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
                self.room = "praia"
                self.describe_room()
                return
            self.say(f"Bem-vindo, {self.char.name}! Digite 'entrar' para comecar.")
            return

        # Ajuda
        if cmd in ("ajuda", "help", "?"):
            self.say("Comandos: olhar | ir <norte/sul/leste/oeste> | pegar <item> | " \
            "inventario | limpar | status")
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
            self.say(f"Inventario: {self.char.inventory if self.char.inventory else 'vazio'}")
            self.say(f"Status: {self.char.status}")
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
            self.room = r["exits"][direction]
            self.describe_room()
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