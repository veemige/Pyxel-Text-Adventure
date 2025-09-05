import pyxel as px
from game.constants import WIDTH, HEIGHT, TEXT_COLOR
from game.state import GameState
from game.logic import GameLogic
from game.rendering import GameRenderer


class App:
    def __init__(self):
        px.init(WIDTH, HEIGHT, title="TEXT ADVENTURE")

        # Estado + logica + renderer
        self.state = GameState()
        self.logic = GameLogic(self.state)
        self.renderer = GameRenderer(self.state)

        # Paleta (verde terminal)
        px.colors[TEXT_COLOR] = 0x00FF00

        # Tenta carregar save; senao, mensagem inicial
        if not self.logic.load_game():
            self.state.say("Bem-vindo! Digite seu nome e pressione Enter. (Use 'ajuda' para dicas)")

        px.run(self.update, self.draw)

    def update(self):
        self.logic.update()

    def draw(self):
        self.renderer.draw()


App()