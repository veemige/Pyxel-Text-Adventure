import random
from .constants import CHAR_H

class CombatState:
    def __init__(self):
        self.in_combat = False
        self.enemy = None
        self.player_status = {}
        self.skill_cd = {}

    def reset(self):
        self.in_combat = False
        self.enemy = None
        self.player_status.clear()
        self.skill_cd.clear()
