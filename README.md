# Pyxel Text Adventure

Projeto em Python usando Pyxel (engine retro) com layout de aventura de texto:
- Metade superior: cenario pixelizado.
- Metade inferior: console de texto com historico, quebra de linha e prompt.

## Recursos
- Janela 320x240 (4:3) e paleta com texto verde (indice 11 ajustado para 0x00FF00).
- Console com historico, quebra de linha por palavras, cursor piscando.
- Entrada de teclado: letras a-z, digitos 0-9, espaco, backspace com repeticao, Enter.
- Comandos de jogo:
	- `ajuda | help | ?` — lista os comandos.
	- `olhar | look | l` — descreve a sala atual.
	- `ir | go <norte/sul/leste/oeste>` — move entre salas.
	- `pegar | take <item>` — coleta itens do local.
	- `inventario | inv | i` — mostra o que voce carrega.
	- `limpar | clear | cls` — limpa o historico do console.
- Mundo inicial com 3 salas: `praia`, `floresta`, `caverna` e itens `concha`, `tocha`.
- Cenas simples desenhadas por codigo (sol e mar, arvores, entrada da caverna).

Observacao: As mensagens do jogo estao em ASCII (sem acentos) para compatibilidade com a fonte padrao do Pyxel.

## Como executar
Requisitos: Python 3.x e Pyxel instalado.

Windows PowerShell:

```powershell
python -m pip install pyxel
python .\main.py
```

Atalhos do Pyxel: `ESC` para sair, `ALT+ENTER` para alternar tela cheia (se suportado).

## Estrutura
```
main.py      # codigo do jogo
README.md    # este arquivo
```

## Acentos e fonte customizada (opcional)
O jogo inclui um caminho opcional para renderizar acentos via atlas bitmap (mapa `EXT_FONT_MAP`).
Se voce quiser usar acentos mais tarde, adicione um `assets.pyxres` com os glifos 4x6 na imagem 0
nas coordenadas indicadas no mapa e altere os textos para incluir os caracteres acentuados.

## Proximos passos
- Adicionar mais salas, puzzles e estados.
- Comandos extra: usar/abrir/examinar.
- Salvar/carregar jogo.
- Fonte personalizada com acentos (via atlas) ou UI com tilemap.
- Sons/efeitos e pequenas animacoes no cenario.