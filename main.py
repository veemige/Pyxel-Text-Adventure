import pyxel as px
import os
import zipfile
from game.constants import WIDTH, HEIGHT, TEXT_COLOR
from game.state import GameState
from game.logic import GameLogic
from game.rendering import GameRenderer


class App:
    def __init__(self):
        px.init(WIDTH, HEIGHT, title="CORPO SECO")
        # Carrega recursos (.pyxres) e inicia a música, com caminho absoluto e logs
        self._load_resources()

        # Estado + logica + renderer
        self.state = GameState()
        self.logic = GameLogic(self.state)
        self.renderer = GameRenderer(self.state)

        # Paleta (verde terminal)
        px.colors[TEXT_COLOR] = 0x00FF00

        # Tenta carregar save; senao, mensagem inicial
        if not self.logic.load_game():
            self.state.say("Digite seu nome e pressione Enter. ('ajuda' para dicas)")

        px.run(self.update, self.draw)

    def update(self):
        self.logic.update()

    def draw(self):
        self.renderer.draw()

    def _load_resources(self):
        """Carrega o arquivo .pyxres e tenta tocar a música 0 (se existir)."""
        base_dir = os.path.dirname(__file__)
        cwd = os.getcwd()
        print(f"[assets] base_dir={base_dir}")
        print(f"[assets] cwd={cwd}")
        candidates = [
            os.path.join(base_dir, "assets", "game.pyxres"),
            os.path.join(cwd, "assets", "game.pyxres"),
            os.path.join(base_dir, "game.pyxres"),
            os.path.join(cwd, "game.pyxres"),
        ]
        # Se não achar pelos nomes padrão, tente qualquer .pyxres dentro de assets
        for root in (os.path.join(base_dir, "assets"), os.path.join(cwd, "assets")):
            if os.path.isdir(root):
                for name in os.listdir(root):
                    if name.lower().endswith(".pyxres"):
                        candidates.append(os.path.join(root, name))
        loaded = False
        for path in candidates:
            path = os.path.normpath(path)
            print(f"[assets] tentando: {path}")
            if os.path.exists(path):
                # Verifica se o arquivo parece ser um ZIP válido (pyxres é um zip)
                if not zipfile.is_zipfile(path):
                    print(f"[assets] arquivo corrompido/nao-zip: {path}")
                    continue
                try:
                    px.load(path)
                    print(f"[assets] carregado: {path}")
                    loaded = True
                    break
                except BaseException as e:
                    print(f"[assets] falha ao carregar {path}: {e}")
        if not loaded:
            print("[assets] nenhum .pyxres encontrado nos caminhos candidatos.")
            # Criar um .pyxres minimo em assets/game.pyxres
            target_dir = os.path.join(base_dir, "assets")
            os.makedirs(target_dir, exist_ok=True)
            out_path = os.path.join(target_dir, "game.pyxres")
            try:
                self._generate_default_pyxres(out_path)
                # Tenta carregar o que acabou de gerar
                if os.path.exists(out_path) and zipfile.is_zipfile(out_path):
                    px.load(out_path)
                    print(f"[assets] gerado e carregado: {out_path}")
                    loaded = True
                else:
                    print(f"[assets] falha ao gerar .pyxres valido em: {out_path}")
            except BaseException as e:
                print(f"[assets] erro ao gerar .pyxres: {e}")
            if not loaded:
                return

        # Tenta tocar alguma música; percorre alguns índices comuns
        started = False
        for idx in range(0, 16):
            try:
                px.playm(idx, loop=True)
                print(f"[audio] music {idx} tocando (loop)")
                started = True
                break
            except BaseException:
                continue
        if not started:
            print("[audio] nenhuma music encontrada (0..15). Verifique no editor do Pyxel se há trilha salva.")
            # Fallback opcional: gera um beep simples para validar áudio
            try:
                s = px.sound(0)
                s.set("c2c3c4c5", "s", "7", "n", 25)
                px.play(0, [0], loop=True)
                print("[audio] fallback: sound 0 gerado e tocando (loop)")
            except BaseException as e:
                print(f"[audio] fallback sound falhou: {e}")

    def _generate_default_pyxres(self, out_path: str):
        """Gera um recurso Pyxel minimo com sound 0 e music 0 e salva em out_path."""
        # Som simples para teste
        s = px.sound(0)
        # notas, timbre (s: square), volume (0-7), efeito (n: none), speed (ticks)
        s.set("c2d2e2g2c3", "s", "77777", "n", 25)
        # Música 0 tocando sfx 0 no canal 0
        m = px.music(0)
        m.set([[0]])
        # Salva o recurso
        px.save(out_path)
        print(f"[assets] default .pyxres salvo em: {out_path}")

if __name__ == "__main__":
    App()