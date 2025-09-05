from .character import Character
from .items import ITEMS, ITEM_POSITIONS
from .world import WORLD
from .encounters import ENCOUNTERS, SCRIPTED_BY_ROOM
from .constants import WIDTH, CHAR_W


class GameState:
    """Encapsula todo o estado do jogo."""

    def __init__(self):
        # Componentes principais
        self.char = Character()

        # Dados do mundo carregados dos módulos
        self.item_map = ITEMS
        self.item_positions = ITEM_POSITIONS
        self.rooms = WORLD
        self.encounters = ENCOUNTERS
        self.scripted_by_room = SCRIPTED_BY_ROOM

        # Estado da sessão
        self.room = "menu"
        self.awaiting_name = True
        self.history = []
        self.input_buf = ""
        # Largura maxima de caracteres por linha no console (margens de 6px)
        self.max_cols = (WIDTH - 12) // CHAR_W

        # Efeitos e flags
        self.effects = set()
        self.encounter_flags = set()
        self.encounter_chance = 0.25

        # Estado de combate
        self.in_combat = False
        self.enemy = None
        self.player_status = {}
        self.skill_cd = {}

    # --------- Utilidades de texto/console ---------
    def say(self, text: str):
        for raw in text.split("\n"):
            self.history.extend(self._wrap(raw, self.max_cols))

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
