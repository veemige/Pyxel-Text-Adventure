import pyxel as px
import random
from game.items import ITEMS as EXTERNAL_ITEMS, ITEM_POSITIONS as EXTERNAL_ITEM_POSITIONS
from game.world import WORLD as EXTERNAL_WORLD
from game.encounters import ENCOUNTERS as EXTERNAL_ENCOUNTERS, SCRIPTED_BY_ROOM as EXTERNAL_SCRIPTED
from game.character import Character

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

...

class App:
    def __init__(self):
        px.init(WIDTH, HEIGHT, title="TEXT ADVENTURE")

        # Personagem
        self.char = Character()

        # Paleta (verde terminal)
        px.colors[TEXT_COLOR] = 0x00FF00

        # Console / UI
        self.history = []
        self.input_buf = ""
        self.ext_map = EXT_FONT_MAP

        # Efeitos e status
        self.effects = set()           # ex.: {"tocha"}
        self.player_status = {}        # ex.: {"guard": 1}
        self.skill_cd = {}             # ex.: {"sangrar": 2}

        # Dados vindos dos modulos (itens, mundo, posicoes)
        self.item_map = EXTERNAL_ITEMS
        self.rooms = EXTERNAL_WORLD
        self.room = "menu"
        self.awaiting_name = True
        self.item_positions = EXTERNAL_ITEM_POSITIONS

        # Estado de progresso
        self.visited_rooms = set()

        # Console: largura maxima (margens de 6px)
        self.max_cols = (WIDTH - 12) // CHAR_W

        # Mensagens iniciais
        self.say("Bem-vindo! Digite seu nome e pressione Enter. (Use 'ajuda' para dicas)")
        self.describe_room()

        # Encontros (modulo)
        self.encounter_chance = 0.25
        self.encounters = EXTERNAL_ENCOUNTERS
        self.scripted_by_room = EXTERNAL_SCRIPTED
        self.encounter_flags = set()

        # Combate
        self.in_combat = False
        self.enemy = None

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
                    self.say("Digite um nome e pressione Enter. Ou 'entrar' para manter 'Heroi'.")
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

        # Em combate: restringe comandos
        if self.in_combat:
            if cmd in ("ajuda", "help", "?"):
                self.say("Em combate: atacar | leve | pesado | defender | sangrar | atordoar | usar <item> | fugir | status | inventario")
                return
            if cmd in ("status", "info"):
                self.say(f"Nome: {self.char.name}")
                self.say(f"Vida: {self.char.status['vida']}/{self.char.status['vida_max']} | Energia: {self.char.status['energia']}/{self.char.status['energia_max']}")
                if self.enemy:
                    self.say(f"Inimigo: {self.enemy['name']} {self.enemy['hp']}/{self.enemy['max_hp']}")
                return
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
            if cmd in ("atacar", "attack", "a"):
                self._combat_attack(mode="normal")
                return
            if cmd in ("leve", "ataque leve", "atacar leve"):
                self._combat_attack(mode="leve")
                return
            if cmd in ("pesado", "ataque pesado", "atacar pesado"):
                self._combat_attack(mode="pesado")
                return
            if cmd in ("defender", "defesa", "block"):
                self._combat_defend()
                return
            if cmd in ("sangrar", "sangue"):
                self._combat_skill_bleed()
                return
            if cmd in ("atordoar", "stun"):
                self._combat_skill_stun()
                return
            if cmd.startswith("usar ") or cmd.startswith("use "):
                _, _, item = cmd.partition(" ")
                before = self.char.status["vida"]
                self.use(item.strip())
                # Se combate ainda ativo e inimigo vivo, turno do inimigo
                if self.in_combat and self.enemy and self.enemy["hp"] > 0 and self.char.status["vida"] > 0:
                    self._combat_enemy_turn()
                return
            if cmd in ("fugir", "run", "escape"):
                if random.random() < 0.5:
                    self.say("Voce fugiu do combate.")
                    self.in_combat = False
                    self.enemy = None
                else:
                    self.say("Nao conseguiu fugir!")
                    if self.enemy and self.char.status["vida"] > 0:
                        self._combat_enemy_turn()
                return
            self.say("Voce esta em combate. Use: atacar | leve | pesado | defender | sangrar | atordoar | usar <item> | fugir | status")
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
            energia = self.char.status["energia"]; emax = self.char.status["energia_max"]
            self.say(f"Nivel {lvl} | XP {xp}/{to_next} | Pontos {pts}")
            self.say(f"Atributos: Vida {vida}/{vmax}, Forca {forca}, Defesa {defesa}, Energia {energia}/{emax}")
            # Mostrar efeitos ativos
            effects = ", ".join(sorted(self.effects)) if self.effects else "nenhum"
            self.say(f"Efeitos: {effects}")
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
        if self.in_combat:
            self.say("Nao pode se mover em combate.")
            return
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
            # Ativa efeito especial da tocha
            if item == "tocha":
                if "tocha" in self.effects:
                    self.say("A tocha ja esta acesa.")
                else:
                    self.effects.add("tocha")
                    self.say("A tocha agora esta acesa. Voce pode entrar na caverna.")
        else:
            self.say("Nao pode usar isso.")

    # ------- Entrada em sala (concede XP apenas na primeira vez) -------
    def enter_room(self, new_room: str):
        # Bloqueia entrar no INTERIOR da caverna sem tocha ativa
        if new_room == "interior da caverna" and "tocha" not in self.effects:
            self.say("Esta muito escuro para entrar. Use a tocha primeiro: 'usar tocha'.")
            return
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
        if self.in_combat:
            return
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
        self._start_combat(eid, data)
    
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

    # ----------------- Combate -----------------
    def _start_combat(self, encounter_id: str, enemy_def: dict):
        if self.in_combat:
            return
        lvl = self.char.status["nivel"]
        name = enemy_def.get("name", "Inimigo")
        base_hp = int(enemy_def.get("base_hp", 5))
        atk = int(enemy_def.get("atk", 1))
        dfn = int(enemy_def.get("def", 0))
        hp = base_hp + max(0, lvl - 1)
        self.enemy = {
            "id": encounter_id,
            "name": name,
            "hp": hp,
            "max_hp": hp,
            "atk": atk,
            "def": dfn,
            "level": max(1, lvl),
            "status": {},  # ex.: {"sangrando": 2, "atordoado": 1}
        }
        self.in_combat = True
        self.say(f"Um {name} aparece! Combate iniciado.")
        self.say("Seu turno: atacar | leve | pesado | defender | sangrar | atordoar | usar <item> | fugir.")
        # Regenera um pouco de energia ao entrar em combate
        self._regen_energy(1)

    def _combat_player_attack(self):
        # Mantido por compatibilidade com comando 'atacar'
        self._combat_attack(mode="normal")

    def _combat_attack(self, mode: str = "normal"):
        if not self.in_combat or not self.enemy:
            return
        # Parametros por modo
        if mode == "leve":
            hit_chance = 0.95; mult = 0.7; cost = 0
        elif mode == "pesado":
            hit_chance = 0.65; mult = 1.8; cost = 3
        else:
            hit_chance = 0.85; mult = 1.0; cost = 0
        # Energia
        if cost > 0 and not self._spend_energy(cost):
            self.say(f"Sem energia suficiente ({self.char.status['energia']}/{self.char.status['energia_max']}).")
            return
        # Acerto
        if random.random() > hit_chance:
            self.say(f"Seu ataque {mode} errou!")
            # Turno do inimigo
            if self.enemy and self.enemy["hp"] > 0 and self.char.status["vida"] > 0:
                self._combat_enemy_turn()
            return
        # Dano
        p_for = self.char.status["forca"]
        e_def = self.enemy.get("def", 0)
        base = max(1, int(round(p_for * mult)) - e_def)
        dmg = max(1, base)
        # critico simples 10%
        if random.random() < 0.10:
            dmg += 1
            self.say("Acerto critico!")
        self.enemy["hp"] = max(0, self.enemy["hp"] - dmg)
        self.say(f"Voce ataca ({mode}) e causa {dmg} de dano. ({self.enemy['hp']}/{self.enemy['max_hp']})")
        if self.enemy["hp"] <= 0:
            self._end_combat(victory=True)
            return
        # inimigo revida
        if self.char.status["vida"] > 0:
            self._combat_enemy_turn()

    def _combat_defend(self):
        # Reduz o proximo dano pela metade e regenera energia extra
        self.player_status["guard"] = 1
        self.say("Voce assume postura defensiva.")
        self._regen_energy(2)
        if self.enemy and self.enemy["hp"] > 0 and self.char.status["vida"] > 0:
            self._combat_enemy_turn()

    def _combat_skill_bleed(self):
        # Requer arma cortante (adaga), custo de energia e cooldown
        if self.skill_cd.get("sangrar", 0) > 0:
            self.say(f"'Sangrar' em recarga por {self.skill_cd['sangrar']} turno(s).")
            return
        if "adaga" not in self.char.inventory["armas"]:
            self.say("Voce precisa de uma arma cortante (ex.: adaga).")
            return
        if not self._spend_energy(2):
            self.say("Sem energia suficiente.")
            return
        # Aplica DOT no inimigo
        cur = self.enemy["status"].get("sangrando", 0)
        self.enemy["status"]["sangrando"] = max(cur, 0) + 3
        self.say("Voce causa um corte profundo! (sangrar 3)")
        self.skill_cd["sangrar"] = 3
        if self.enemy and self.enemy["hp"] > 0 and self.char.status["vida"] > 0:
            self._combat_enemy_turn()

    def _combat_skill_stun(self):
        # Tenta atordoar (chance moderada), custo e cooldown
        if self.skill_cd.get("atordoar", 0) > 0:
            self.say(f"'Atordoar' em recarga por {self.skill_cd['atordoar']} turno(s).")
            return
        if not self._spend_energy(3):
            self.say("Sem energia suficiente.")
            return
        # Pequena vantagem se tiver arma
        chance = 0.45
        if self.char.inventory["armas"]:
            chance += 0.10
        if random.random() < chance:
            cur = self.enemy["status"].get("atordoado", 0)
            self.enemy["status"]["atordoado"] = max(cur, 0) + 1
            self.say("Voce atordoa o inimigo! (perde o proximo turno)")
        else:
            self.say("Tentativa de atordoar falhou.")
        self.skill_cd["atordoar"] = 4
        if self.enemy and self.enemy["hp"] > 0 and self.char.status["vida"] > 0:
            self._combat_enemy_turn()

    def _combat_enemy_turn(self):
        if not self.in_combat or not self.enemy:
            return
        # Aplica status no inicio do turno do inimigo (DOT, etc.)
        if self.enemy["status"].get("sangrando", 0) > 0:
            self.enemy["hp"] = max(0, self.enemy["hp"] - 1)
            self.enemy["status"]["sangrando"] -= 1
            self.say(f"{self.enemy['name']} sangra (1). ({self.enemy['hp']}/{self.enemy['max_hp']})")
            if self.enemy["status"]["sangrando"] <= 0:
                del self.enemy["status"]["sangrando"]
        # Morreu por DOT
        if self.enemy["hp"] <= 0:
            self._end_combat(victory=True)
            return
        # Atordoado: perde o turno
        if self.enemy["status"].get("atordoado", 0) > 0:
            self.say(f"{self.enemy['name']} esta atordoado e perde o turno!")
            self.enemy["status"]["atordoado"] -= 1
            if self.enemy["status"]["atordoado"] <= 0:
                del self.enemy["status"]["atordoado"]
            # Fim do turno do inimigo: regenera energia e avanca cooldowns
            self._regen_energy(1)
            self._cooldowns_step()
            return
        e_atk = self.enemy.get("atk", 1)
        p_def = self.char.status["defesa"]
        dmg = max(1, e_atk - p_def)
        # Guard ativa reduz dano pela metade (arredonda para baixo)
        if self.player_status.get("guard", 0) > 0:
            red = dmg // 2
            dmg = max(0, dmg - red)
            self.player_status["guard"] -= 1
            if self.player_status["guard"] <= 0:
                del self.player_status["guard"]
        self.char.status["vida"] = max(0, self.char.status["vida"] - dmg)
        self.say(f"{self.enemy['name']} ataca e causa {dmg} de dano. (Sua vida: {self.char.status['vida']}/{self.char.status['vida_max']})")
        if self.char.status["vida"] <= 0:
            self.say("Voce caiu em combate.")
        # Fim do turno do inimigo: regenera energia e avanca cooldowns
        self._regen_energy(1)
        self._cooldowns_step()

    def _end_combat(self, victory: bool):
        if victory:
            # Recompensa simples de XP
            base_hp = self.enemy.get("max_hp", 5)
            atk = self.enemy.get("atk", 1)
            xp = max(1, base_hp // 2 + atk)
            self.say(f"Vitoria! Você ganha {xp} XP.")
            for m in self.char.gain_xp(xp):
                self.say(m)
        else:
            self.say("Combate encerrado.")
        self.in_combat = False
        self.enemy = None
        self.player_status.clear()
        # Peq. recuperacao fora de combate
        self._regen_energy(1)

    # ---------- Utilidades de combate ----------
    def _spend_energy(self, cost: int) -> bool:
        if self.char.status["energia"] < cost:
            return False
        self.char.status["energia"] -= cost
        return True
    
    def _regen_energy(self, amount: int):
        e = self.char.status["energia"]
        emax = self.char.status["energia_max"]
        self.char.status["energia"] = min(emax, e + amount)
    
    def _cooldowns_step(self):
        # Reduz cooldowns ativos em 1
        if not self.skill_cd:
            return
        for k in list(self.skill_cd.keys()):
            if self.skill_cd[k] > 0:
                self.skill_cd[k] -= 1
            if self.skill_cd[k] <= 0:
                self.skill_cd[k] = 0

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
        items = self.rooms[self.room].get("items", [])
        cx = x + w // 2
        base = y + h - 30

        # Menu (titulo simples)
        if scene == "menu":
            title = "TEXT ADVENTURE"
            # caixa central
            px.rectb(cx - 70, y + 18, 140, 24, 6)
            self._draw_text_mixed(cx - len(title)*CHAR_W//2, y + 26, title, 7)
            subtitle = "Digite seu nome e Enter"
            self._draw_text_mixed(cx - len(subtitle)*CHAR_W//2, y + 60, subtitle, 7)
            # nenhum item no menu
            return

        if scene == "praia":
            px.circ(cx + 70, y + 20, 10, 13)
            px.rect(x, base - 20, w, 20, 12)   # mar (azul claro)
            px.rect(x, y + h - 30, w, 30, 15)   # areia (bege)
            # Desenha itens da sala (se presentes)
            self._draw_room_items(x, y, w, h, items)

        elif scene == "floresta":
            for i in range(5):
                tx = x + 20 + i * 50
                px.rect(tx, base - 25, 6, 25, 4)   # tronco (marrom)
                px.tri(tx - 10, base - 10, tx + 3, base - 75, tx + 16, base - 10, 11)  # copa (verde claro)
            # itens
            self._draw_room_items(x, y, w, h, items)
        elif scene == "caverna":
            px.tri(cx - 70, base, cx - 40, base - 70, cx - 25, base, 0)
            px.tri(cx + 25, base, cx + 40, base - 70, cx + 70, base, 0)
            px.tri(cx - 35, base, cx, base - 90, cx + 35, base, 0)
            px.circ(cx, base - 20, 45, 0)
            px.rect(x, y + h - 30, w, 30, 3)
            px.rect(x, base, w, 30, 3)
            # Desenha itens da sala (se presentes)
            self._draw_room_items(x, y, w, h, items)
        elif scene == "interior da caverna":
            # Salas sem 'scene' especifica: desenhar por nome
            # interior escuro com estalagmites/estalactites
            px.rect(x, y, w, h, 0)
            # estalactites
            for i in range(0, w, 20):
                px.tri(x + i, y, x + i + 8, y + 14, x + i + 16, y, 1)
            # estalagmites
            floor_y = y + h - 10
            for i in range(10, w, 24):
                px.tri(x + i, floor_y, x + i + 8, floor_y - 12, x + i + 16, floor_y, 1)
            # brilho ao norte
            px.circ(x + w - 20, y + 10, 4, 7)
            # itens
            self._draw_room_items(x, y, w, h, items)
        elif scene == "planicie":
            # ceu estrelado
            for sx in range(x + 5, x + w - 5, 16):
                if (sx // 7) % 2 == 0:
                    px.pset(sx, y + 8, 7)
            # colinas
            px.tri(x, base, x + 50, base - 18, x + 100, base, 3)
            px.tri(x + 90, base, x + 140, base - 14, x + 190, base, 3)
            # gramados
            for gx in range(x + 8, x + w - 8, 12):
                px.pset(gx, base - 4, 11)
                px.pset(gx + 1, base - 6, 11)
            self._draw_room_items(x, y, w, h, items)
        elif scene == "leste da vila":
            road_y = y + h - 18
            # estrada
            px.rect(x, road_y, w, 8, 4)
            # casas simples
            hx = x + 20
            for k in range(3):
                px.rect(hx + k * 50, road_y - 20, 30, 20, 5)
                px.tri(hx + k * 50, road_y - 20, hx + k * 50 + 15, road_y - 32, hx + k * 50 + 30, road_y - 20, 2)
                # janela
                px.pset(hx + k * 50 + 8, road_y - 10, 10)
                px.pset(hx + k * 50 + 9, road_y - 10, 10)
            self._draw_room_items(x, y, w, h, items)

    def _draw_room_items(self, x, y, w, h, items_in_room):
        room = self.room
        positions = self.item_positions.get(room, {})
        for item in items_in_room:
            pos = positions.get(item)
            if not pos:
                continue
            ix, iy = pos
            self._draw_item(item, ix, iy)

    def _draw_item(self, item: str, ix: int, iy: int):
        # Representacao simples por formas
        if item == "concha":
            # pequena concha branca/rosa
            px.pset(ix - 2, iy, 7)
            px.pset(ix - 1, iy, 15)
            px.pset(ix, iy, 7)
            px.pset(ix + 1, iy, 7)
        elif item == "galho":
            # galho marrom
            px.line(ix - 6, iy, ix + 6, iy - 2, 4)
            px.pset(ix + 2, iy - 3, 11)
        elif item == "tocha":
            # cabo
            px.rect(ix - 1, iy, 3, 8, 4)
            # chama
            px.tri(ix - 3, iy, ix + 3, iy, ix, iy - 6, 10)
            px.pset(ix, iy - 7, 8)
        elif item == "adaga":
            # lamina cinza e punho escuro
            px.line(ix - 3, iy, ix + 3, iy, 6)
            px.pset(ix - 4, iy, 5)

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