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
			title = "TEXT ADVENTURE"
			px.rectb(cx - 70, y + 18, 140, 24, 6)
			draw_text_mixed(cx - len(title)*CHAR_W//2, y + 26, title, 7)
			subtitle = "Digite seu nome e Enter"
			draw_text_mixed(cx - len(subtitle)*CHAR_W//2, y + 60, subtitle, 7)
			return

		if scene == "praia":
			px.circ(cx + 70, y + 20, 10, 13)
			px.rect(x, base - 20, w, 20, 12)
			px.rect(x, y + h - 30, w, 30, 15)
			self._draw_room_items(x, y, w, h, items)
		elif scene == "floresta":
			for i in range(5):
				tx = x + 20 + i * 50
				px.rect(tx, base - 25, 6, 25, 4)
				px.tri(tx - 10, base - 10, tx + 3, base - 75, tx + 16, base - 10, 11)
			self._draw_room_items(x, y, w, h, items)
		elif scene == "caverna":
			px.tri(cx - 70, base, cx - 40, base - 70, cx - 25, base, 0)
			px.tri(cx + 25, base, cx + 40, base - 70, cx + 70, base, 0)
			px.tri(cx - 35, base, cx, base - 90, cx + 35, base, 0)
			px.circ(cx, base - 20, 45, 0)
			px.rect(x, y + h - 30, w, 30, 3)
			px.rect(x, base, w, 30, 3)
			self._draw_room_items(x, y, w, h, items)
		elif scene == "interior da caverna":
			px.rect(x, y, w, h, 0)
			for i in range(0, w, 20):
				px.tri(x + i, y, x + i + 8, y + 14, x + i + 16, y, 1)
			floor_y = y + h - 10
			for i in range(10, w, 24):
				px.tri(x + i, floor_y, x + i + 8, floor_y - 12, x + i + 16, floor_y, 1)
			px.circ(x + w - 20, y + 10, 4, 7)
			self._draw_room_items(x, y, w, h, items)
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
			px.pset(ix - 2, iy, 7)
			px.pset(ix - 1, iy, 15)
			px.pset(ix, iy, 7)
			px.pset(ix + 1, iy, 7)
		elif item == "galho":
			px.line(ix - 6, iy, ix + 6, iy - 2, 4)
			px.pset(ix + 2, iy - 3, 11)
		elif item == "tocha":
			px.rect(ix - 1, iy, 3, 8, 4)
			px.tri(ix - 3, iy, ix + 3, iy, ix, iy - 6, 10)
			px.pset(ix, iy - 7, 8)
		elif item == "adaga":
			px.line(ix - 3, iy, ix + 3, iy, 6)
			px.pset(ix - 4, iy, 5)

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
