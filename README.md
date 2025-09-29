# CORPO SECO — Pyxel Text Adventure
# versão BETA

Aventura de texto com visual retro (Pyxel). Metade de cima desenha a cena; metade de baixo é um console com histórico e prompt.

• Resolução: `320x240`  • Divisória: `SPLIT_Y = 120`  • Cor do texto: índice `11` (verde)

Observação: os textos em jogo (console) usam ASCII simples (sem acentos). Este README usa acentos normalmente.

## Como executar
Requisitos: Python 3.x e Pyxel.

Windows PowerShell:

```powershell
python -m pip install pyxel
python .\main.py
```

Atalhos do Pyxel: `ESC` para sair, `ALT+ENTER` para alternar tela cheia (se suportado).

## Comandos do jogo (exploração)
- `ajuda | help | ?` — lista os comandos disponíveis.
- `olhar | look | l` — descreve a sala atual, itens e saídas.
- `ir | go <norte/sul/leste/oeste/...>` — move para uma saída da sala.
- `pegar | take <item>` — pega um item do chão para o inventário.
- `inventario | inv | i` — mostra inventário por categorias.
- `descricao | desc <item>` — mostra a descrição do item.
- `usar | use <item>` — usa um utensílio/consumível (ex.: tocha, poção de vida).
- `equipar | equip <item>` — equipa arma/armadura (aplica bônus de dano/defesa).
- `status | info` — mostra atributos, XP, nível, pontos e efeitos ativos.
- `visitadas | visited` — lista as salas que você já visitou.
- `limpar | clear | cls` — limpa o histórico do console.
- `salvar` — salva a sessão em `savegame.json`.
- `sair | exit | quit` — salva e fecha o jogo.

Comandos da loja (quando um mercador abrir a loja):
- `lista` — mostra o catálogo do vendedor com preços.
- `comprar <item> [qtd]` — compra 1 ou mais unidades (se tiver moedas suficientes).
- `vender <item> [qtd]` — vende itens do seu inventário (recebe ~50% do preço base).
- `sair` — fecha a loja.

Menu inicial:
- `entrar` — entra no jogo na sala `praia` (ou defina um nome digitando e depois use `entrar`).
- `nome <novo>` — altera seu nome ainda no menu.

Comandos de debug (opcionais):
- `encontros` — mostra se encontros estão ativos na sala, região e encontros elegíveis.
- `forcar encontro <id>` — dispara um encontro específico imediatamente.
- `chance <0..1>` — ajusta a chance base de encontros aleatórios (padrão `0.25`).
- Atalho: segurar `SHIFT` dá `+10 XP` (debug).

## Mecânicas principais

### Progressão, XP e Level Up
- XP por exploração: ao entrar em uma sala pela primeira vez você ganha `+2 XP`.
- XP por combate: ao vencer, ganha XP proporcional ao inimigo: `xp = max(1, max_hp // 2 + atk)`.
- Níveis: XP para próximo nível é linear: `10, 20, 30, ...` (fórmula: `10 + 10*(nível-1)`).
- Ao subir de nível: `+2 pontos de habilidade`, `+2 vida máxima` e vida totalmente restaurada.

Pontos de habilidade (distribuição via comando):
- `atribuir <vida|forca|defesa> <qtd>`
	- `vida`: cada ponto dá `+2 vida máxima` e cura `+2` imediatamente.
	- `forca`: cada ponto dá `+1` de Força.
	- `defesa`: cada ponto dá `+1` de Defesa.

Atributos relevantes do personagem:
- `vida/vida_max`, `forca`, `defesa`, `nivel`, `experiencia`, `pontos` (distribuíveis), `energia/energia_max`, `agilidade`, `moedas`.

### Moedas, loja e saques (loot)
- Moedas: mostradas no `status`. Você ganha moedas ao vencer inimigos (cada encontro define um intervalo `gold_drop`).
- Loja (mercador): alguns encontros de NPC abrem uma loja com catálogo e preços. Você pode comprar e vender.
	- Compra: paga o preço listado do vendedor para cada unidade.
	- Venda: recebe 50% do preço base (definido no vendedor ou no item, se possuir `preco`). O mercador não compra itens sem preço conhecido.
	- Exemplo de catálogo do mercador costeiro: `pocao de vida (5)`, `adaga (12)`, `armadura leve (25)`.

### Itens, inventário, uso e equipamento
Categorias de inventário: `utensilios`, `armas`, `armaduras`, `comuns`.
- `pegar <item>` move o item da sala para a categoria adequada.
- `usar <item>` aplica efeitos de utensílios/consumíveis.
	- `tocha`: ativa efeito de iluminação.
	- `pocao de vida`: recupera `3` de vida e é consumida.
- `equipar <item>` aplica bônus:
	- Armas: aumentam `forca` em `dano` do item enquanto equipadas.
	- Armaduras: aumentam `defesa` conforme o `slot` (`head/body/legs/feet`).

Comando de inspeção:
- `descricao <item>` — imprime a descrição cadastrada do item.

### Encontros (aleatórios e programados)
- Encontros aleatórios acontecem ao entrar numa sala com `"encounters_enabled": true` e passam em um teste de probabilidade (`encounter_chance`, padrão `0.25`).
- Elegibilidade por região/sala e nível: cada encontro define `regions` e opcional `rooms`, além de `min_level/max_level`.
- Escolha ponderada: entre os elegíveis, o jogo escolhe 1 encontro pelo seu `weight` relativo.
- Encontros programados por sala: `SCRIPTED_BY_ROOM` mapeia eventos com `id`, `type`, `min_level`, `handler` e `once` (se `true`, acontece só uma vez por sessão; usa flags internas).

Fluxo ao entrar em uma sala:
1) Ganha XP se for a primeira visita (uma única vez por sala).
2) Descrição da sala, itens e saídas.
3) Encontros programados elegíveis (e não repetidos quando `once`).
4) Possível encontro aleatório se a sala permitir e a rolagem de chance passar.

Encontros disponíveis (arquivo `game/encounters.py`):
- `mercador_costeiro` (npc) — regiões: praia/planície/vila — `weight: 1` — abre a loja (compra/venda).
- `caranguejo` (enemy) — região: praia — `min_level: 1`, `max_level: 3`, `weight: 3` — dropa moedas e pode soltar `concha`.
- `lobo` (enemy) — regiões: floresta/planície — `min_level: 2`, `weight: 2` — dropa moedas e pode soltar `couro`.
- `morcego` (enemy) — região: caverna — `min_level: 1`, `weight: 2` — dropa moedas e pode soltar `dente`.

### Combate tático simples
Inicia em encontros de tipo `enemy`.

Ações do jogador:
- `atacar` (normal): chance de acerto ~85%, multiplicador de dano `1.0`, custo de energia `2`.
- `leve`: ~95% de acerto, multiplicador `0.7`, custo `1`.
- `pesado`: ~65% de acerto, multiplicador `1.8`, custo `3`.
- `defender`: aplica guarda por 1 turno (reduz cerca de metade do dano recebido), regenera `+2` de energia.
- `sangrar`: requer arma cortante (ex.: `adaga` no inventário), custo `2`, aplica status `sangrando (3)` no inimigo, recarga `3` turnos.
- `atordoar`: custo `3`, chance base `45%` (+10% se possuir qualquer arma), aplica `atordoado (1)`, recarga `4` turnos.
- `usar <item>`: consome o turno, aplica efeito (se aplicável), então o inimigo age.
- `fugir`: 50% de chance de escapar; se falhar, o inimigo age.

Detalhes:
- Dano: usa `forca` (com bônus de arma) e defesa do inimigo; 10% de crítico (+1 dano).
- Status inimigo: `sangrando` (drena 1 de HP por turno por N turnos), `atordoado` (perde 1 turno).
- Energia: ações gastam energia; o turno inimigo e algumas ações regeneram energia.
- Fim do combate: vitória concede XP; derrota encerra com mensagem e você pode morrer.

### Morte, salvar e carregar
- Se `vida <= 0`, a tela indica sua morte; pressione `Enter` para carregar o último save.
- `salvar` grava `savegame.json` com: personagem, sala atual, salas, flags de encontros, efeitos ativos e estado do menu.
- `sair` salva e encerra o jogo.

## Mundo (salas, regiões, encontros)
As salas ficam em `game/world_data.json`.

Campos de sala:
- `desc`, `exits`, `items`, `scene`, `region`, `encounters_enabled`.

Salas existentes (arquivo `game/world_data.json`):
- `menu` — região: menu — encontros: OFF
- `praia` — saídas: `norte: floresta`, `leste: entrada da caverna` — região: praia — encontros: OFF — itens: `concha`
- `floresta` — saídas: `sul: praia`, `norte: floresta profunda` — região: floresta — encontros: ON — itens: `galho`
- `entrada da caverna` — saídas: `oeste: praia`, `entrada: caverna` — região: caverna — encontros: ON — itens: (nenhum)
- `caverna` — saídas: `sul: entrada da caverna`, `norte: planicie` — região: caverna — encontros: ON — itens: `capacete de mineiro`, `remo`
- `planicie` — saídas: `sul: caverna`, `oeste: floresta profunda`, `norte: leste da vila` — região: planicie — encontros: ON — itens: (nenhum)
- `floresta profunda` — saídas: `sul: floresta`, `leste: planicie`, `norte: vila` — região: floresta — encontros: ON — itens: `galho`
- `leste da vila` — saídas: `sul: planicie`, `oeste: vila` — região: vila — encontros: ON — itens: `adaga`
- `vila` — saídas: `leste: leste da vila`, `oeste: rio`, `sul: floresta profunda` — região: vila — encontros: OFF — itens: `pocao de vida`, `tocha`
- `rio` — saídas: `leste: vila`, `sul: ?` — região: rio — encontros: ON — itens: (nenhum)

## Itens (definições e locais iniciais)
Arquivo: `game/item_data.json`.

Definições (arquivo `game/item_data.json`):
- `concha` — tipo: comum — "Uma concha do mar."
- `galho` — tipo: arma — dano `0.5` — "Um galho seco."
- `tocha` — tipo: utensílio — efeito: ilumina o ambiente.
- `adaga` — tipo: arma — dano `1.0` — "Uma adaga afiada."
- `pocao de vida` — tipo: consumível — restaura 3 de vida.
- `capacete de mineiro` — tipo: armadura — `defesa: 1.0` — `slot: head`.
- `remo` — tipo: utensílio — permite navegar/atravessar áreas com barco (rio → end).
- `camiseta do e-colab` — tipo: armadura — `defesa: 20` — `slot: torso` (drop raro).
- `couro` — tipo: comum — material.
- `dente` — tipo: comum — troféu simples.
- `vara de pesca` — tipo: arma — `dano: 1.2`.

Posições iniciais (coordenadas de desenho na cena):
- `praia`: `concha` em `(160, 108)`
- `floresta`: `galho` em `(40, 112)`
- `floresta profunda`: `galho` em `(40, 112)`
- `leste da vila`: `adaga` em `(200, 104)`
- `vila`: `pocao de vida` em `(200, 104)`, `tocha` em `(190, 102)`
- `caverna`: `capacete de mineiro` em `(120, 90)`, `remo` em `(190, 90)`

## Interface e renderização
- Metade superior desenha a cena com formas simples (sol, mar, árvores, casas, cavernas, etc.).
- Os itens são desenhados com sprites minimalistas gerados por código nas posições do JSON.
- Metade inferior exibe o console com histórico, quebra de linha por palavras e cursor piscando.
 - Durante encontros: NPCs e inimigos aparecem como sprites simples na cena; somem ao fechar a loja ou ao fim do combate/morte.

## Customização rápida
- Salas/mundo: edite `game/world_data.json` (adicione chaves `region` e `encounters_enabled` nas salas novas).
- Itens: edite `game/item_data.json` (`definitions` e `positions`).
- Encontros: edite `game/encounters.py` (tabela `ENCOUNTERS`) e ajuste regiões/nível/`weight`.
- Eventos programados: `SCRIPTED_BY_ROOM` (use `once: true` para disparar uma única vez por sessão).
- Probabilidade de encontros: ajuste em tempo de execução com `chance <valor>` ou altere `encounter_chance` padrão em `game/state.py`.

## Estrutura do projeto
```
Pyxel-Text-Adventure/
	main.py
	game/
		constants.py
		state.py
		logic.py
		rendering.py
		render.py
		font.py
		character.py
		items.py
		item_data.json
		world.py
		world_data.json
		encounters.py
```

## Problemas conhecidos e dicas
- Para atravessar o `rio` até `end`, tenha o `remo` no inventário.
- Fugir pode falhar (50%). Guarde energia para habilidades.
- Para depurar encontros, use `encontros` e `forcar encontro <id>`.

---
Divirta-se explorando, lutando e evoluindo no mundo de CORPO SECO!