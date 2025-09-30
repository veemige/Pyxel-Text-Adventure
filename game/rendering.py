import pyxel as px
from .constants import WIDTH, HEIGHT, SPLIT_Y, TEXT_COLOR, BG_COLOR, CHAR_W, CHAR_H
from .render import draw_text_mixed


class GameRenderer:
	def __init__(self, state):
		self.state = state

	def draw(self):
		px.cls(BG_COLOR)

		# Metade de cima: cenario
		self.draw_scene(0, 0, WIDTH, SPLIT_Y)

		# Separador
		px.rect(0, SPLIT_Y, WIDTH, 1, TEXT_COLOR)

		# Metade de baixo: console de texto
		self.draw_console(0, SPLIT_Y + 1, WIDTH, HEIGHT - (SPLIT_Y + 1))

	def draw_scene(self, x, y, w, h):
		s = self.state
		# Ceu e chao base
		if s.awaiting_name and s.room == "menu" or s.room != "interior da caverna":
			px.rect(x, y, w, h, 1)
			px.rect(x, y + h - 30, w, 30, 3)

		scene = s.rooms[s.room]["scene"]
		items = s.rooms[s.room].get("items", [])
		cx = x + w // 2
		base = y + h - 30

		if scene == "menu":
			title = "CORPO SECO"
			# Calcula largura total do texto pixelizado (5 pixels por char * scale * número de chars)
			title_width = len(title) * 5 * 2  # 5 pixels de largura por char, scale=2
			title_x = cx - title_width // 2
			
			# Caixa bem maior ao redor do título
			box_padding = 20
			box_height = 35
			box_y = y + 30
			px.rectb(title_x - box_padding, box_y, title_width + box_padding * 2, box_height, 7)
			
			# Centraliza o texto verticalmente dentro da caixa
			text_height = 5 * 2  # altura do texto com scale=2 (5 pixels * 2)
			text_y = box_y + (box_height - text_height) // 2
			self.draw_pixel_text(title_x, text_y, title, 6, scale=2)
			return

		if scene == "praia":
			px.circ(cx + 70, y + 20, 10, 13)
			px.rect(x, base - 20, w, 20, 12)
			px.rect(x, y + h - 30, w, 30, 15)
			self._draw_room_items(x, y, w, h, items)
			self._draw_active_entity(x, y, w, h)
		elif scene == "floresta":
			for i in range(5):
				tx = x + 20 + i * 50
				px.rect(tx, base - 25, 6, 25, 4)
				px.tri(tx - 10, base - 10, tx + 3, base - 75, tx + 16, base - 10, 11)
			self._draw_room_items(x, y, w, h, items)
			self._draw_active_entity(x, y, w, h)
		elif scene == "entrada da caverna":
			px.tri(cx - 70, base, cx - 40, base - 70, cx - 25, base, 0)
			px.tri(cx + 25, base, cx + 40, base - 70, cx + 70, base, 0)
			px.tri(cx - 35, base, cx, base - 90, cx + 35, base, 0)
			px.circ(cx, base - 20, 45, 0)
			px.rect(x, y + h - 30, w, 30, 3)
			px.rect(x, base, w, 30, 3)
			self._draw_room_items(x, y, w, h, items)
			self._draw_active_entity(x, y, w, h)
		elif scene == "caverna":
			px.rect(x, y, w, h, 0)
			for i in range(0, w, 20):
				px.tri(x + i, y, x + i + 8, y + 14, x + i + 16, y, 1)
			floor_y = y + h - 10
			for i in range(10, w, 24):
				px.tri(x + i, floor_y, x + i + 8, floor_y - 12, x + i + 16, floor_y, 1)
			px.circ(x + w - 20, y + 10, 4, 7)
			self._draw_room_items(x, y, w, h, items)
			self._draw_active_entity(x, y, w, h)
		elif scene == "planicie":
			for sx in range(x + 5, x + w - 5, 16):
				if (sx // 7) % 2 == 0:
					px.pset(sx, y + 8, 7)
			px.tri(x, base, x + 50, base - 18, x + 100, base, 3)
			px.tri(x + 90, base, x + 140, base - 14, x + 190, base, 3)
			for gx in range(x + 8, x + w - 8, 12):
				px.pset(gx, base - 4, 11)
				px.pset(gx + 1, base - 6, 11)
			self._draw_room_items(x, y, w, h, items)
			self._draw_active_entity(x, y, w, h)
		elif scene == "leste da vila":
			road_y = y + h - 18
			px.rect(x, road_y, w, 8, 4)
			hx = x + 20
			for k in range(3):
				px.rect(hx + k * 50, road_y - 20, 30, 20, 5)
				px.tri(hx + k * 50, road_y - 20, hx + k * 50 + 15, road_y - 32, hx + k * 50 + 30, road_y - 20, 2)
				px.pset(hx + k * 50 + 8, road_y - 10, 10)
				px.pset(hx + k * 50 + 9, road_y - 10, 10)
			self._draw_room_items(x, y, w, h, items)
			self._draw_active_entity(x, y, w, h)
		elif scene == "vila":
			px.rect(x, base - 20, w, 20, 4)
			hx = x + 20
			for k in range(3):
				px.rect(hx + k * 50, base - 40, 30, 20, 5)
				px.tri(hx + k * 50, base - 40, hx + k * 50 + 15, base - 52, hx + k * 50 + 30, base - 40, 2)
				px.pset(hx + k * 50 + 8, base - 30, 10)
				px.pset(hx + k * 50 + 9, base - 30, 10)
			self._draw_room_items(x, y, w, h, items)
			self._draw_active_entity(x, y, w, h)
		elif scene == "floresta profunda":
			for i in range(7):
				tx = x + 10 + i * 40
				px.rect(tx, base - 25, 6, 25, 4)
				px.tri(tx - 10, base - 10, tx + 3, base - 75, tx + 16, base - 10, 11)
			self._draw_room_items(x, y, w, h, items)
			self._draw_active_entity(x, y, w, h)
		elif scene == "rio":
			px.rect(x, base - 20, w, 20, 1)
			for i in range(0, w, 20):
				px.tri(x + i, base - 10, x + i + 8, base - 22, x + i + 16, base - 10, 3)
			# barco
			px.rect(cx - 20, base - 5, 40, 7, 9)
			px.tri(cx - 25, base - 5, cx, base + 1, cx + 25, base - 5, 9)
			px.line(cx, base - 5, cx, base - 3, 7)
			px.line(cx - 20, base - 5, cx - 20, base - 3, 7)
			self._draw_room_items(x, y, w, h, items)
			self._draw_active_entity(x, y, w, h)
		elif scene == "end":
			px.rect(x, y, w, h, 1)
			px.rect(x, y + h - 30, w, 30, 3)
			self.draw_pixel_text(cx - 60, base - 50, "Continua...", 10, scale=3)
			self.draw_pixel_text(cx - 50, base - 20, "Feito por Joao Melo", 7, scale=1)
			# Normalmente não há entities em 'end', mas deixado como está.

	def _draw_room_items(self, x, y, w, h, items_in_room):
		s = self.state
		positions = s.item_positions.get(s.room, {})
		for item in items_in_room:
			pos = positions.get(item)
			if not pos:
				continue
			ix, iy = pos
			self._draw_item(item, ix, iy)

	def _draw_item(self, item: str, ix: int, iy: int):
		if item == "concha":
			px.rect(ix - 2, iy, 4, 1, 7)
			px.pset(ix - 1, iy, 15)
			px.rect(ix - 1, iy - 1, 2, 1, 7)
		elif item == "galho":
			px.line(ix - 6, iy, ix + 6, iy - 2, 4)
			px.pset(ix + 2, iy - 3, 11)
		elif item == "tocha":
			px.rect(ix - 1, iy, 3, 8, 4)
			px.tri(ix - 3, iy, ix + 3, iy, ix, iy - 6, 7)
			px.pset(ix, iy - 7, 6)
		elif item == "adaga":
			px.pset(ix - 4, iy, 5)
			px.line(ix - 3, iy, ix + 3, iy, 6)
		elif item == "pocao de vida":
			px.circ(ix - 2, iy - 4, 5, 8)
			px.pset(ix - 1, iy - 5, 7)
			px.pset(ix + 1, iy - 5, 7)
			px.rect(ix - 3, iy - 14, 3, 5, 6)
		elif item == "capacete de mineiro":
			px.rect(ix - 5, iy - 3, 10, 4, 8)
			px.rect(ix - 3, iy - 7, 6, 4, 9)
			px.pset(ix, iy - 8, 7)
		elif item == "remo":
			px.line(ix - 6, iy, ix + 6, iy, 4)
			px.line(ix - 2, iy - 3, ix + 2, iy + 3, 4)
			px.rect(ix - 11, iy - 1, 5, 3, 4)
			px.pset(ix, iy, 7)

	def draw_console(self, x, y, w, h):
		s = self.state
		margin = 6
		max_rows = (h - margin * 2) // CHAR_H
		visible_rows = max(1, max_rows - 1)

		lines = s.history[-visible_rows:]

		ty = y + margin
		for line in lines:
			draw_text_mixed(x + margin, ty, line, TEXT_COLOR)
			ty += CHAR_H

		cursor = "_" if (px.frame_count // 15) % 2 == 0 else " "
		prompt = f"> {s.input_buf}{cursor}"
		draw_text_mixed(x + margin, y + h - margin - CHAR_H, prompt, TEXT_COLOR)


	def draw_pixel_text(self, x, y, text, color, scale=2):
		"""Desenha texto grande usando retângulos como pixels"""
		
		# Mapeamento simples de algumas letras (você pode expandir)
		font_map = {
			'C': [[0,1,1,0], [1,0,0,0], [1,0,0,0], [1,0,0,0], [0,1,1,0]],
			'O': [[0,1,1,0], [1,0,0,1], [1,0,0,1], [1,0,0,1], [0,1,1,0]],
			'R': [[1,1,1,0], [1,0,0,1], [1,1,1,0], [1,0,1,0], [1,0,0,1]],
			'P': [[1,1,1,0], [1,0,0,1], [1,1,1,0], [1,0,0,0], [1,0,0,0]],
			'S': [[0,1,1,1], [1,0,0,0], [0,1,1,0], [0,0,0,1], [1,1,1,0]],
			'E': [[1,1,1,1], [1,0,0,0], [1,1,1,0], [1,0,0,0], [1,1,1,1]],
			'D': [[1,1,1,0], [1,0,0,1], [1,0,0,1], [1,0,0,1], [1,1,1,0]],
			'A': [[0,1,1,0], [1,0,0,1], [1,1,1,1], [1,0,0,1], [1,0,0,1]],
			'T': [[1,1,1,1], [0,1,0,0], [0,1,0,0], [0,1,0,0], [0,1,0,0]],
			'J': [[0,0,1,1], [0,0,0,1], [0,0,0,1], [1,0,0,1], [0,1,1,0]],
			'M': [[1,0,0,0,1], [1,1,0,1,1], [1,0,1,0,1], [1,0,0,0,1], [1,0,0,0,1]],
			'L': [[1,0,0,0], [1,0,0,0], [1,0,0,0], [1,0,0,0], [1,1,1,1]],
			'N': [[1,0,0,1], [1,1,0,1], [1,0,1,1], [1,0,0,1], [1,0,0,1]],
			'I': [[1,1,1], [0,1,0], [0,1,0], [0,1,0], [1,1,1]],
			'U': [[1,0,0,1], [1,0,0,1], [1,0,0,1], [1,0,0,1], [0,1,1,0]],
			'F': [[1,1,1,1], [1,0,0,0], [1,1,1,0], [1,0,0,0], [1,0,0,0]],
			'P': [[1,1,1,0], [1,0,0,1], [1,1,1,0], [1,0,0,0], [1,0,0,0]],
			' ': [[0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0]],
		}
		
		char_x = x
		for char in text.upper():
			if char in font_map:
				pattern = font_map[char]
				for row_idx, row in enumerate(pattern):
					for col_idx, pixel in enumerate(row):
						if pixel:
							px.rect(
								char_x + col_idx * scale, 
								y + row_idx * scale, 
								scale, scale, 
								color
							)
			
			char_x += 5 * scale  # Espaçamento entre caracteres

	def _draw_active_entity(self, x, y, w, h):
		s = self.state
		entity = getattr(s, "active_entity", None)
		room_tag = getattr(s, "active_entity_room", None)
		if not entity or room_tag != s.room:
			return

		base = y + h - 30
		cx = x + w // 2
		etype = entity.get("type")
		eid = entity.get("id", "").lower()
		name = entity.get("name", "").upper()

		# animação simples
		bob = self._sprite_bob()

		# sombra no chão
		self._draw_shadow(cx, base, 14 if etype == "enemy" else 10)

		# sprite
		if etype == "npc":
			self._draw_npc(cx, base + bob)
		elif etype == "enemy":
			if "caranguejo" in eid:
				self._draw_enemy_crab(cx, base + bob)
			elif "lobo" in eid:
				self._draw_enemy_wolf(cx, base + bob)
			elif "morcego" in eid:
				self._draw_enemy_bat(cx, base + bob)
			elif "pescador" in eid:
				self._draw_enemy_fisher(cx, base + bob)
			elif "thales" in eid:
				self._draw_enemy_thales(cx, base + bob)
			else:
				self._draw_enemy_generic(cx, base + bob)

		# nome com leve sombra
		px.text(cx - len(name) * 2 + 1, base - 27, name[:18], 0)
		px.text(cx - len(name) * 2,     base - 28, name[:18], 7)

	# ---------- helpers visuais ----------
	def _sprite_bob(self):
		# ciclo: 0,1,0,-1
		step = (px.frame_count // 8) % 4
		return (1 if step == 1 else (-1 if step == 3 else 0))

	def _draw_shadow(self, cx, base, half_w=10):
		# sombra achatada (retângulo fino)
		px.rect(cx - half_w, base - 2, half_w * 2, 2, 1)

	# ---------- sprites caprichados ----------
	def _draw_npc(self, cx, base, bob=0):
		# pernas
		px.rect(cx - 5, base - 10, 3, 10, 5)
		px.rect(cx + 2, base - 10, 3, 10, 5)
		# botas
		px.rect(cx - 6, base - 2, 5, 2, 0)
		px.rect(cx + 1, base - 2, 5, 2, 0)
		# torso
		px.rect(cx - 7, base - 22, 14, 12, 12)     # casaco
		px.rectb(cx - 7, base - 22, 14, 12, 0)     # contorno
		px.rect(cx - 7, base - 16, 14, 2, 3)       # cinto
		# braços
		px.rect(cx - 10, base - 20, 3, 7, 12)
		px.rect(cx + 7, base - 20, 3, 7, 12)
		# cabeça
		px.circ(cx, base - 26, 4, 7)
		# chapéu
		px.rect(cx - 8, base - 30, 16, 2, 9)
		px.rect(cx - 5, base - 33, 10, 3, 9)
		# detalhes rosto
		px.pset(cx - 2, base - 27, 0); px.pset(cx + 2, base - 27, 0)
		px.pset(cx, base - 25, 8)

	def _draw_enemy_generic(self, cx, base, bob=0):
		# corpo e cabeça
		px.rect(cx - 8, base - 14, 16, 10, 8)
		px.circ(cx + 6, base - 18, 4, 6)
		# olhos
		px.pset(cx + 5, base - 19, 7); px.pset(cx + 7, base - 19, 7)
		# garras/patas
		px.rect(cx - 10, base - 6, 4, 3, 5)
		px.rect(cx + 6,  base - 6, 4, 3, 5)
		# contorno
		px.rectb(cx - 8, base - 14, 16, 10, 0)

	def _draw_enemy_crab(self, cx, base, bob=0):
		# casco
		px.rect(cx - 12, base - 9, 24, 7, 8)
		px.rectb(cx - 12, base - 9, 24, 7, 0)
		# olhos
		px.rect(cx - 4, base - 12, 3, 3, 7); px.pset(cx - 3, base - 13, 0)
		px.rect(cx + 2, base - 12, 3, 3, 7); px.pset(cx + 3, base - 13, 0)
		# garras
		px.tri(cx - 16, base - 7, cx - 8, base - 13, cx - 2, base - 7, 8)
		px.tri(cx + 16, base - 7, cx + 8, base - 13, cx + 2, base - 7, 8)
		# patas
		for dx in (-10, -6, -2, 2, 6, 10):
			px.pset(cx + dx, base - 2, 7)
			px.pset(cx + dx + (1 if dx < 0 else -1), base - 1, 7)

	def _draw_enemy_wolf(self, cx, base, bob=0):
		# corpo
		px.rect(cx - 14, base - 12, 24, 9, 5)
		px.rectb(cx - 14, base - 12, 24, 9, 0)
		# cabeça + focinho
		px.rect(cx + 8, base - 14, 10, 8, 5)
		px.tri(cx + 18, base - 10, cx + 26, base - 9, cx + 18, base - 7, 5)
		# orelhas
		px.tri(cx + 9, base - 14, cx + 12, base - 20, cx + 15, base - 14, 5)
		px.tri(cx + 15, base - 14, cx + 18, base - 20, cx + 21, base - 14, 5)
		# cauda
		px.tri(cx - 16, base - 10, cx - 24, base - 8, cx - 16, base - 6, 5)
		# pernas
		px.rect(cx - 10, base - 3, 3, 3, 5)
		px.rect(cx - 2,  base - 3, 3, 3, 5)
		px.rect(cx + 6,  base - 3, 3, 3, 5)
		# olhos
		px.pset(cx + 15, base - 12, 7); px.pset(cx + 12, base - 12, 7)
		# focinho claro
		px.rect(cx + 18, base - 9, 4, 3, 6)

	def _draw_enemy_bat(self, cx, base, bob=0):
		# amplitude de asa animada
		flap = 3 if ((px.frame_count // 6) % 2 == 0) else 0
		# corpo
		px.circ(cx, base - 14, 4, 13)
		# asas
		px.tri(cx, base - 14, cx - 18, base - (8 + flap), cx - 6, base - 6, 0)
		px.tri(cx, base - 14, cx + 18, base - (8 + flap), cx + 6, base - 6, 0)
		# olhos
		px.pset(cx - 1, base - 15, 7); px.pset(cx + 1, base - 15, 7)
		# orelhas
		px.tri(cx - 2, base - 18, cx - 1, base - 22, cx, base - 18, 13)
		px.tri(cx + 2, base - 18, cx + 1, base - 22, cx, base - 18, 13)

	def _draw_enemy_fisher(self, cx, base, bob=0):
		# pernas
		px.rect(cx - 4, base - 10, 3, 10, 3)
		px.rect(cx + 1, base - 10, 3, 10, 3)
		# torso e braços
		px.rect(cx - 6, base - 22, 12, 12, 11)
		px.rectb(cx - 6, base - 22, 12, 12, 0)
		px.rect(cx - 9, base - 20, 3, 8, 11)
		px.rect(cx + 6, base - 20, 3, 8, 11)
		# cabeça + chapéu
		px.circ(cx, base - 26, 4, 7)
		px.rect(cx - 7, base - 30, 14, 2, 9)
		px.tri(cx - 3, base - 30, cx + 3, base - 30, cx, base - 34, 9)
		# vara e linha
		px.line(cx + 6, base - 18, cx + 20, base - 32, 7)
		px.line(cx + 20, base - 32, cx + 20, base - 16, 7)

	def _draw_enemy_thales(self, cx, base, bob=0):
		# capa
		px.tri(cx - 18, base - 10, cx, base - 30, cx + 18, base - 10, 2)
		# tronco
		px.rect(cx - 10, base - 24, 20, 16, 2)
		px.rectb(cx - 10, base - 24, 20, 16, 0)
		# cabeça
		px.circ(cx, base - 28, 5, 7)
		# “coroa”
		px.rect(cx - 8, base - 33, 16, 2, 8)
		px.tri(cx - 6, base - 33, cx - 4, base - 38, cx - 2, base - 33, 8)
		px.tri(cx + 2, base - 33, cx + 4, base - 38, cx + 6, base - 33, 8)
		# olhos brilhando
		px.pset(cx - 2, base - 29, 10); px.pset(cx + 2, base - 29, 10)
		# braços
		px.rect(cx - 13, base - 22, 3, 10, 2)
		px.rect(cx + 10, base - 22, 3, 10, 2)