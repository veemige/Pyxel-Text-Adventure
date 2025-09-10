import pyxel as px
from .constants import CHAR_H, CHAR_W, TEXT_COLOR
from .font import EXT_FONT_MAP


def draw_text_mixed(x: int, y: int, s: str, col: int):
    cx = x
    for ch in s:
        if ch in EXT_FONT_MAP:
            u, v = EXT_FONT_MAP[ch]
            px.blt(cx, y, 0, u, v, CHAR_W, CHAR_H, 0)
            cx += CHAR_W
        else:
            px.text(cx, y, ch, col)
            cx += CHAR_W