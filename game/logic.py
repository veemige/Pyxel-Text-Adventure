import json
import os
import random
import pyxel as px
from .encounters import weighted_choice as enc_weighted_choice


class GameLogic:
	def __init__(self, state):
		self.s = state

	# --------------- Loop ---------------
	def update(self):
		self.handle_text_input()
		if self.s.char.status["vida"] <= 0:
			self.s.say("Voce morreu!")
			self.s.say("Aperte [ENTER] para carregar o ultimo save.")
			if px.btnp(px.KEY_RETURN):
				self.load_game()

	def handle_text_input(self):
		# Letras a-z
		for k, ch in self._alpha_keymap().items():
			if px.btnp(k):
				self.s.input_buf += ch
		# Numeros e espaco
		for k, ch in self._digit_space_keymap().items():
			if px.btnp(k):
				self.s.input_buf += ch
		# Backspace
		if px.btnp(px.KEY_BACKSPACE, 10, 2) and self.s.input_buf:
			self.s.input_buf = self.s.input_buf[:-1]
		# Enter
		if px.btnp(px.KEY_RETURN):
			cmd = self.s.input_buf.strip().lower()
			if cmd:
				self.s.say(f"> {cmd}")
				self.process_command(cmd)
			self.s.input_buf = ""
		# Debug XP
		if px.btnp(px.KEY_LSHIFT):
			for m in self.s.char.gain_xp(10):
				self.s.say(m)

	# --------------- Comandos ---------------
	def process_command(self, cmd: str):
		s = self.s
		if s.room == "menu":
			if s.awaiting_name:
				if cmd in ("ajuda", "help", "?"):
					s.say("Digite um nome e pressione Enter. Ou 'entrar' para manter 'Heroi'.")
					return
				if cmd == "entrar":
					s.awaiting_name = False
					self.enter_room("praia")
					return
				if cmd and cmd not in ("sair", "exit", "quit"):
					s.char.name = cmd
					s.awaiting_name = False
					s.say(f"Nome definido: {s.char.name}. Digite 'entrar' para comecar.")
					return
				return
			if cmd in ("ajuda", "help", "?"):
				s.say("Menu: entrar | nome <novo> | ajuda")
				return
			if cmd.startswith("nome "):
				_, _, newname = cmd.partition(" ")
				if newname:
					s.char.name = newname
					s.say(f"Nome alterado para {s.char.name}.")
				else:
					s.say("Use: nome <novo_nome>")
				return
			if cmd == "entrar":
				self.enter_room("praia")
				return
			s.say(f"Bem-vindo, {s.char.name}! Digite 'entrar' para comecar.")
			return

		if s.in_combat:
			if cmd in ("ajuda", "help", "?"):
				s.say("Em combate: atacar | leve | pesado | defender | sangrar | atordoar | usar <item> | fugir | status | inventario")
				return
			if cmd in ("status", "info"):
				s.say(f"Nome: {s.char.name}")
				s.say(f"Vida: {s.char.status['vida']}/{s.char.status['vida_max']} | Energia: {s.char.status['energia']}/{s.char.status['energia_max']}")
				if s.enemy:
					s.say(f"Inimigo: {s.enemy['name']} {s.enemy['hp']}/{s.enemy['max_hp']}")
				return
			if cmd in ("inventario", "inv", "i"):
				inv = s.char.inventory
				if inv:
					s.say("Voce carrega: ")
					s.say("Utensilios: " + ", ".join(inv["utensilios"]) if inv["utensilios"] else "Utensilios: vazio")
					s.say("Armas: " + ", ".join(inv["armas"]) if inv["armas"] else "Armas: vazio")
					s.say("Armaduras: " + ", ".join(inv["armaduras"]) if inv["armaduras"] else "Armaduras: vazio")
					s.say("Comuns: " + ", ".join(inv["comuns"]) if inv["comuns"] else "Comuns: vazio")
				else:
					s.say("Voce nao carrega nada.")
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
				self.use(item.strip())
				if s.in_combat and s.enemy and s.enemy["hp"] > 0 and s.char.status["vida"] > 0:
					self._combat_enemy_turn()
				return
			if cmd in ("fugir", "run", "escape"):
				if random.random() < 0.5:
					s.say("Voce fugiu do combate.")
					s.in_combat = False
					s.enemy = None
				else:
					s.say("Nao conseguiu fugir!")
					if s.enemy and s.char.status["vida"] > 0:
						self._combat_enemy_turn()
				return
			s.say("Voce esta em combate. Use: atacar | leve | pesado | defender | sangrar | atordoar | usar <item> | fugir | status")
			return

		if cmd in ("ajuda", "help", "?"):
			s.say("Comandos: olhar | ir <norte/sul/leste/oeste> | pegar <item> | inventario | pontos | atribuir <vida|forca|defesa> <qtd> | limpar | status | salvar")
			return
		if cmd in ("olhar", "look", "l"):
			self.describe_room()
			return
		if cmd.startswith("ir ") or cmd.startswith("go "):
			_, _, rest = cmd.partition(" ")
			self.go(rest.strip())
			return
		if cmd.startswith("pegar ") or cmd.startswith("take "):
			_, _, item = cmd.partition(" ")
			self.take(item.strip())
			return
		if cmd in ("inventario", "inv", "i"):
			inv = s.char.inventory
			if inv:
				s.say("Voce carrega: ")
				s.say("Utensilios: " + ", ".join(inv["utensilios"]) if inv["utensilios"] else "Utensilios: vazio")
				s.say("Armas: " + ", ".join(inv["armas"]) if inv["armas"] else "Armas: vazio")
				s.say("Armaduras: " + ", ".join(inv["armaduras"]) if inv["armaduras"] else "Armaduras: vazio")
				s.say("Comuns: " + ", ".join(inv["comuns"]) if inv["comuns"] else "Comuns: vazio")
			else:
				s.say("Voce nao carrega nada.")
			return
		if cmd in ("visitadas", "visited"):
			if s.char.visited_rooms:
				s.say("Salas visitadas: " + ", ".join(s.char.visited_rooms))
			else:
				s.say("Voce nao visitou nenhuma sala.")
			return
		if cmd == "encontros":
			r = s.rooms[s.room]
			region = r.get("region")
			enabled = r.get("encounters_enabled", False)
			pool = self._eligible_encounters()
			ids = [eid for eid, _ in pool]
			s.say(f"Encontros aqui: {'ON' if enabled else 'OFF'} | Regiao: {region}")
			s.say("Elegiveis: " + (", ".join(ids) if ids else "nenhum"))
			s.say(f"Chance base: {s.encounter_chance:.2f}")
			return
		if cmd.startswith("forcar encontro "):
			_, _, eid = cmd.partition("forcar encontro ")
			eid = eid.strip()
			if eid:
				self.trigger_encounter(eid)
			else:
				s.say("Use: forcar encontro <id>")
			return
		if cmd.startswith("chance "):
			try:
				val = float(cmd.split()[1])
				s.encounter_chance = max(0.0, min(1.0, val))
				s.say(f"Chance de encontro ajustada para {s.encounter_chance:.2f}")
			except Exception:
				s.say("Use: chance <valor entre 0 e 1>")
			return
		if cmd in ("limpar", "clear", "cls"):
			s.history.clear()
			return
		if cmd == "salvar":
			self.save_game()
			return
		if cmd in ("sair", "exit", "quit"):
			self.save_game()
			s.say("Jogo salvo.")
			px.quit()
		if cmd in ("status", "info"):
			lvl = s.char.status["nivel"]
			xp = s.char.status["experiencia"]
			to_next = s.char.xp_to_next()
			pts = s.char.status["pontos"]
			vida = s.char.status["vida"]; vmax = s.char.status["vida_max"]
			forca = s.char.status["forca"]; defesa = s.char.status["defesa"]
			energia = s.char.status["energia"]; emax = s.char.status["energia_max"]
			s.say(f"Nome: {s.char.name}")
			s.say(f"Localizacao: {s.room}")
			s.say(f"Nivel {lvl} | XP {xp}/{to_next} | Pontos {pts}")
			s.say(f"Atributos: Vida {vida}/{vmax}, Forca {forca}, Defesa {defesa}, Energia {energia}/{emax}")
			effects = ", ".join(sorted(s.effects)) if s.effects else "nenhum"
			s.say(f"Efeitos: {effects}")
			return
		if cmd.startswith("usar ") or cmd.startswith("use "):
			_, _, item = cmd.partition(" ")
			self.use(item.strip())
			return
		if cmd.startswith("equipar ") or cmd.startswith("equip "):
			_, _, item = cmd.partition(" ")
			self.equip(item.strip())
			return

		s.say("Nao entendi. Digite 'ajuda'.")


	# --------------- Acoes ---------------
	def describe_room(self):
		s = self.s
		r = s.rooms[s.room]
		s.say(r["desc"])
		if r["items"]:
			s.say("Ao redor: " + ", ".join(r["items"]))
		if r["exits"]:
			s.say("Saidas: " + ", ".join(sorted(r["exits"].keys())))

	def go(self, direction: str):
		s = self.s
		if s.in_combat:
			s.say("Nao pode se mover em combate.")
			return
		r = s.rooms[s.room]
		if direction in r["exits"]:
			self.enter_room(r["exits"][direction])
		else:
			s.say("Voce nao pode ir por ai.")

	def take(self, item: str):
		s = self.s
		if not item:
			s.say("Pegar o que?")
			return
		r = s.rooms[s.room]
		inv = s.char.inventory
		if item in r["items"]:
			r["items"].remove(item)
			info = s.item_map.get(item, {"tipo": "comum"})
			tipo = info.get("tipo")
			if tipo == "utensilio":
				inv["utensilios"].append(item)
			elif tipo == "arma":
				inv["armas"].append(item)
			elif tipo == "armadura":
				inv["armaduras"].append(item)
			else:
				inv["comuns"].append(item)
			s.say(f"Voce pegou a {item}.")
			for m in s.char.gain_xp(3):
				s.say(m)
		else:
			s.say("Nao vejo isso aqui.")

	def use(self, item: str):
		s = self.s
		if not item:
			s.say("Usar o que?")
			return
		inv = s.char.inventory
		if item in inv["utensilios"]:
			s.say(f"Voce usou o {item}.")
			info = s.item_map.get(item, {})
			effect = info.get("efeito")
			if effect:
				s.say(f"Voce usou o item {item}: {effect}")
			if item == "tocha":
				if "tocha" in s.effects:
					s.say("A tocha ja esta acesa.")
				else:
					s.effects.add("tocha")
					s.say("A tocha agora esta acesa. Voce pode entrar na caverna.")
			elif item == "pocao de vida":
				self._regen_health(3)
				s.say("Voce bebeu a pocao e restaurou 3 pontos de vida.")
				inv["utensilios"].remove(item)
		else:
			s.say("Nao pode usar isso.")
	
	def equip(self, item: str):
		s = self.s
		if not item:
			s.say("Equipar o que?")
			return
		inv = s.char.inventory
		info = s.item_map.get(item, {})
		dano = info.get("dano", 0)
		if item in inv["armas"]:
			if s.char.equipped_weapon == item:
				s.say(f"{item} ja esta equipado.")
				return
			s.char.equipped_weapon = item
			if dano > 0:
				s.char.status["forca"] += dano
				s.say(f"Voce equipou  {item}, ganhando +{dano} de forca.")
			else:
				s.say(f"Voce equipou  {item}.")
		elif item in inv["armaduras"]:
			slot = info.get("slot")
			defesa = info.get("defesa", 0)
			if not slot:
				s.say(f"{item} nao pode ser equipado.")
				return
			if s.char.equipped_armor.get(slot) == item:
				s.say(f"{item} ja esta equipado.")
				return
			prev = s.char.equipped_armor.get(slot)
			if prev and defesa > 0:
				s.char.status["defesa"] -= info.get("defesa", 0)
				s.say(f"Voce removeu {prev}, perdendo -{defesa} de defesa.")
			s.char.equipped_armor[slot] = item
			if defesa > 0:
				s.char.status["defesa"] += defesa
				s.say(f"Voce equipou {item}, ganhando +{defesa} de defesa.")
			else:
				s.say(f"Voce equipou {item}.")
		else:
			s.say("Voce nao tem isso para equipar.")

	def enter_room(self, new_room: str):
		s = self.s
		if new_room == "interior da caverna" and "tocha" not in s.effects:
			s.say("Esta muito escuro para entrar. Use a tocha primeiro: 'usar tocha'.")
			return
		s.room = new_room
		if new_room not in s.char.visited_rooms:
			s.char.visited_rooms.add(new_room)
			for m in s.char.gain_xp(2):
				s.say(m)
		self.describe_room()
		self._maybe_trigger_scripted_encounter()
		self._maybe_trigger_random_encounter()

	# --------------- Save/Load ---------------
	def save_game(self):
		s = self.s
		save_data = {
			"character": s.char.to_dict(),
			"world_state": {
				"current_room": s.room,
				"rooms_data": s.rooms,
			},
			"game_state": {
				"encounter_flags": list(s.encounter_flags),
				"active_effects": list(s.effects),
				"awaiting_name": s.awaiting_name,
			}
		}
		try:
			with open("savegame.json", "w") as f:
				json.dump(save_data, f, indent=4)
			s.say("Jogo salvo com sucesso.")
		except Exception as e:
			s.say(f"Erro ao salvar: {e}")

	def load_game(self) -> bool:
		s = self.s
		if not os.path.exists("savegame.json"):
			return False
		try:
			with open("savegame.json", "r") as f:
				data = json.load(f)
			s.char.from_dict(data["character"])
			ws = data["world_state"]
			s.room = ws["current_room"]
			s.rooms = ws["rooms_data"]
			gs = data["game_state"]
			s.encounter_flags = set(gs["encounter_flags"])
			s.effects = set(gs["active_effects"])
			s.awaiting_name = gs.get("awaiting_name", False)
			s.in_combat = False
			s.enemy = None
			s.history.clear()
			s.say("Jogo carregado.")
			self.describe_room()
			return True
		except Exception as e:
			s.say(f"Erro ao carregar save: {e}")
			return False

	# --------------- Encontros ---------------
	def _eligible_encounters(self):
		s = self.s
		room = s.room
		region = s.rooms[room].get("region")
		lvl = s.char.status["nivel"]
		pool = []
		for eid, e in s.encounters.items():
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
		s = self.s
		if s.in_combat:
			return
		r = s.rooms[s.room]
		if not r.get("encounters_enabled", False):
			return
		if random.random() >= s.encounter_chance:
			return
		pool = self._eligible_encounters()
		if not pool:
			return
		eid = enc_weighted_choice(pool)
		self.trigger_encounter(eid)

	def _maybe_trigger_scripted_encounter(self):
		s = self.s
		room = s.room
		entries = s.scripted_by_room.get(room, [])
		if not entries:
			return
		lvl = s.char.status["nivel"]
		for e in entries:
			flag = f"script:{e['id']}"
			if e.get("once") and flag in s.encounter_flags:
				continue
			if lvl < e.get("min_level", 1):
				continue
			handler = e.get("handler")
			if handler and hasattr(self, handler):
				getattr(self, handler)()
			else:
				s.say(f"Um evento ocorre: {e['id']}")
			if e.get("once"):
				s.encounter_flags.add(flag)

	def trigger_encounter(self, encounter_id: str):
		s = self.s
		e = s.encounters.get(encounter_id)
		if not e:
			s.say(f"Encontro '{encounter_id}' nao encontrado.")
			return
		if e["type"] == "npc":
			self._enc_npc(encounter_id, e)
		elif e["type"] == "enemy":
			self._enc_enemy(encounter_id, e)
		else:
			s.say(f"Encontro: {encounter_id}")

	def _enc_npc(self, eid, e):
		self.s.say("Um mercador aparece na estrada, oferecendo seus produtos.")
		self.s.say("Dica: voce pode implementar aqui um menu de compra ('comprar <item>').")

	def _enc_enemy(self, eid, e):
		data = e.get("enemy", {})
		self._start_combat(eid, data)

	def script_miner(self):
		self.s.say("Um mineiro cansado surge das sombras: 'Cuidado la dentro.'")

	# --------------- Combate ---------------
	def _start_combat(self, encounter_id: str, enemy_def: dict):
		s = self.s
		if s.in_combat:
			return
		lvl = s.char.status["nivel"]
		name = enemy_def.get("name", "Inimigo")
		base_hp = int(enemy_def.get("base_hp", 5))
		atk = int(enemy_def.get("atk", 1))
		dfn = int(enemy_def.get("def", 0))
		hp = base_hp + max(0, lvl - 1)
		s.enemy = {
			"id": encounter_id,
			"name": name,
			"hp": hp,
			"max_hp": hp,
			"atk": atk,
			"def": dfn,
			"level": max(1, lvl),
			"status": {},
		}
		s.in_combat = True
		s.say(f"Um {name} aparece! Combate iniciado.")
		s.say("Seu turno: atacar | leve | pesado | defender | sangrar | atordoar | usar <item> | fugir.")
		self._regen_energy(1)

	def _combat_attack(self, mode: str = "normal"):
		s = self.s
		if not s.in_combat or not s.enemy:
			return
		if mode == "leve":
			hit_chance = 0.95; mult = 0.7; cost = 1
		elif mode == "pesado":
			hit_chance = 0.65; mult = 1.8; cost = 3
		else:
			hit_chance = 0.85; mult = 1.0; cost = 2
		if cost > 0 and not self._spend_energy(cost):
			s.say(f"Sem energia suficiente ({s.char.status['energia']}/{s.char.status['energia_max']}).")
			return
		if random.random() > hit_chance:
			s.say(f"Seu ataque {mode} errou!")
			if s.enemy and s.enemy["hp"] > 0 and s.char.status["vida"] > 0:
				self._combat_enemy_turn()
			return
		p_for = s.char.status["forca"]
		e_def = s.enemy.get("def", 0)
		base = max(1, int(round(p_for * mult)) - e_def)
		dmg = max(1, base)
		if random.random() < 0.10:
			dmg += 1
			s.say("Acerto critico!")
		s.enemy["hp"] = max(0, s.enemy["hp"] - dmg)
		s.say(f"Voce ataca ({mode}) e causa {dmg} de dano. ({s.enemy['hp']}/{s.enemy['max_hp']})")
		if s.enemy["hp"] <= 0:
			self._end_combat(victory=True)
			return
		if s.char.status["vida"] > 0:
			self._combat_enemy_turn()

	def _combat_defend(self):
		s = self.s
		s.player_status["guard"] = 1
		s.say("Voce assume postura defensiva.")
		self._regen_energy(2)
		if s.enemy and s.enemy["hp"] > 0 and s.char.status["vida"] > 0:
			self._combat_enemy_turn()

	def _combat_skill_bleed(self):
		s = self.s
		if s.skill_cd.get("sangrar", 0) > 0:
			s.say(f"'Sangrar' em recarga por {s.skill_cd['sangrar']} turno(s).")
			return
		if "adaga" not in s.char.inventory["armas"]:
			s.say("Voce precisa de uma arma cortante (ex.: adaga).")
			return
		if not self._spend_energy(2):
			s.say("Sem energia suficiente.")
			return
		cur = s.enemy["status"].get("sangrando", 0)
		s.enemy["status"]["sangrando"] = max(cur, 0) + 3
		s.say("Voce causa um corte profundo! (sangrar 3)")
		s.skill_cd["sangrar"] = 3
		if s.enemy and s.enemy["hp"] > 0 and s.char.status["vida"] > 0:
			self._combat_enemy_turn()

	def _combat_skill_stun(self):
		s = self.s
		if s.skill_cd.get("atordoar", 0) > 0:
			s.say(f"'Atordoar' em recarga por {s.skill_cd['atordoar']} turno(s).")
			return
		if not self._spend_energy(3):
			s.say("Sem energia suficiente.")
			return
		chance = 0.45
		if s.char.inventory["armas"]:
			chance += 0.10
		if random.random() < chance:
			cur = s.enemy["status"].get("atordoado", 0)
			s.enemy["status"]["atordoado"] = max(cur, 0) + 1
			s.say("Voce atordoa o inimigo! (perde o proximo turno)")
		else:
			s.say("Tentativa de atordoar falhou.")
		s.skill_cd["atordoar"] = 4
		if s.enemy and s.enemy["hp"] > 0 and s.char.status["vida"] > 0:
			self._combat_enemy_turn()

	def _combat_enemy_turn(self):
		s = self.s
		if not s.in_combat or not s.enemy:
			return
		if s.enemy["status"].get("sangrando", 0) > 0:
			s.enemy["hp"] = max(0, s.enemy["hp"] - 1)
			s.enemy["status"]["sangrando"] -= 1
			s.say(f"{s.enemy['name']} sangra (1). ({s.enemy['hp']}/{s.enemy['max_hp']})")
			if s.enemy["status"]["sangrando"] <= 0:
				del s.enemy["status"]["sangrando"]
		if s.enemy["hp"] <= 0:
			self._end_combat(victory=True)
			return
		if s.enemy["status"].get("atordoado", 0) > 0:
			s.say(f"{s.enemy['name']} esta atordoado e perde o turno!")
			s.enemy["status"]["atordoado"] -= 1
			if s.enemy["status"]["atordoado"] <= 0:
				del s.enemy["status"]["atordoado"]
			self._regen_energy(1)
			self._cooldowns_step()
			return
		e_atk = s.enemy.get("atk", 1)
		p_def = s.char.status["defesa"]
		dmg = max(1, e_atk - p_def)
		if s.player_status.get("guard", 0) > 0:
			red = dmg // 2
			dmg = max(0, dmg - red)
			s.player_status["guard"] -= 1
			if s.player_status["guard"] <= 0:
				del s.player_status["guard"]
		s.char.status["vida"] = max(0, s.char.status["vida"] - dmg)
		s.say(f"{s.enemy['name']} ataca e causa {dmg} de dano. (Sua vida: {s.char.status['vida']}/{s.char.status['vida_max']})")
		if s.char.status["vida"] <= 0:
			s.say("Voce caiu em combate.")
		self._regen_energy(1)
		self._cooldowns_step()

	def _end_combat(self, victory: bool):
		s = self.s
		if victory:
			base_hp = s.enemy.get("max_hp", 5)
			atk = s.enemy.get("atk", 1)
			xp = max(1, base_hp // 2 + atk)
			s.say(f"Vitoria! Você ganha {xp} XP.")
			for m in s.char.gain_xp(xp):
				s.say(m)
		else:
			s.say("Combate encerrado.")
		s.in_combat = False
		s.enemy = None
		s.player_status.clear()
		self._regen_energy(1)

	# ---------- Utilidades de combate ----------
	def _spend_energy(self, cost: int) -> bool:
		s = self.s
		if s.char.status["energia"] < cost:
			return False
		s.char.status["energia"] -= cost
		return True

	def _regen_energy(self, amount: int):
		s = self.s
		e = s.char.status["energia"]
		emax = s.char.status["energia_max"]
		s.char.status["energia"] = min(emax, e + amount)
	
	def _regen_health(self, amount: int):
		s = self.s
		h = s.char.status["vida"]
		hmax = s.char.status["vida_max"]
		s.char.status["vida"] = min(hmax, h + amount)

	def _cooldowns_step(self):
		s = self.s
		if not s.skill_cd:
			return
		for k in list(s.skill_cd.keys()):
			if s.skill_cd[k] > 0:
				s.skill_cd[k] -= 1
			if s.skill_cd[k] <= 0:
				s.skill_cd[k] = 0

	# ---------- Keymaps ----------
	def _alpha_keymap(self):
		return {
			px.KEY_A: "a", px.KEY_B: "b", px.KEY_C: "c", px.KEY_D: "d",
			px.KEY_E: "e", px.KEY_F: "f", px.KEY_G: "g", px.KEY_H: "h",
			px.KEY_I: "i", px.KEY_J: "j", px.KEY_K: "k", px.KEY_L: "l",
			px.KEY_M: "m", px.KEY_N: "n", px.KEY_O: "o", px.KEY_P: "p",
			px.KEY_Q: "q", px.KEY_R: "r", px.KEY_S: "s", px.KEY_T: "t",
			px.KEY_U: "u", px.KEY_V: "v", px.KEY_W: "w", px.KEY_X: "x",
			px.KEY_Y: "y", px.KEY_Z: "z",
		}

	def _digit_space_keymap(self):
		return {
			px.KEY_SPACE: " ",
			px.KEY_0: "0", px.KEY_1: "1", px.KEY_2: "2", px.KEY_3: "3",
			px.KEY_4: "4", px.KEY_5: "5", px.KEY_6: "6", px.KEY_7: "7",
			px.KEY_8: "8", px.KEY_9: "9",
		}
