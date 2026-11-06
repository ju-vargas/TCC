# Manual dos gráficos do TCC

Regras de cor, textura, marcador e texto para todas as figuras. Uma cor (ou textura, ou
marcador) tem um só significado em todas as figuras. Antes de criar uma figura nova, procure
aqui a entidade; se ela não existir, acrescente a regra neste arquivo antes de usar.

Criado em 2026-11-02. Já seguem tudo: `figuras_descentralizacao.py`, `figuras_perfil_estacao.py`
(comparação de formatos e perfis) e `mapa_cenarios_v4.py` (mapa de pior aumento de SNR).

## 1. Regras gerais

- **Idioma:** inglês em toda a figura (título, eixos, legenda, rótulos), com ponto decimal
  (`2.5`, não `2,5`). O texto do TCC continua em português.
- **Sem verde**, em nenhuma série, faixa ou fundo.
- **Cor nunca sozinha:** toda série tem também um marcador, uma textura ou um rótulo
  escrito. Leitor daltônico e impressão em preto e branco precisam conseguir ler.
- **A cor segue a entidade, não a posição:** se um filtro tira uma série, as outras não
  mudam de cor.
- **Paleta nova só depois de validar:**
  `node <skill dataviz>/scripts/validate_palette.js "<hex,...>" --mode light --pairs all`.
  Cinzas neutros falham no piso de croma de propósito; o resto tem que passar.
- **Saída:** `png` (250 dpi) + `pdf` + `_data.csv` com os números da figura, pela função
  `salvar` de `figuras_analise_grupos.py`.

## 2. Texto e layout

| Item | Regra |
|---|---|
| Fonte | DejaVu Sans (a padrão do matplotlib), peso normal. **Sem negrito.** |
| Fórmulas | `plt.rcParams["mathtext.default"] = "regular"`: K, M, N, C sem itálico |
| Tamanhos | título da figura 9; título de painel 8; eixos 7,5 a 8; marcas e legenda 7; notas 6,5 |
| Cores do texto | `INK_PRIMARY #0b0b0b` (títulos, letras), `INK_SECONDARY #52514e` (eixos, legenda), `INK_MUTED #8a8983` (eixos e linhas de apoio) |
| Fundo | `SURFACE #fcfcfb`; grade `GRID #e4e3df`, fina, só nos eixos que ajudam a ler |
| Largura | 6,3 polegadas (largura do texto na página A4 do TCC) |
| Marcadores de cenário no mapa | rosa forte `#ff3d9a`, sem borda nem halo (amarelo = BCD-MMSE; vermelho lembra erro e a autora recusou); vazado = acima de 0,1 dB, cheio = acima de 3 dB; na legenda, retângulos de cor (vazado e cheio) e só "above 0.1 dB" / "above 3 dB" (sem "vazado:"/"cheio:") |
| Legenda dos cenários no mapa | embaixo, todos os itens numa linha só |
| Barra de cor do mapa | marcas `0.1 dB` e `3 dB` (sem "limit") |
| Lista de configurações nos títulos | sempre em ordem alfabética das letras (1A, 1B, 1E, 1F) |
| Notas de rodapé | não pôr nas figuras principais: o × do mapa e a definição do aumento de SNR ficam no texto do TCC |
| Formato no cabeçalho | o formato em cima (`<22,12>`, fonte 8,5, `INK_PRIMARY`) e o modo embaixo (`RND_ZERO/WRAP`, fonte 7, peso `light`, `INK_SECONDARY`) |
| Eixo de SNR (curvas) | de −10 a 10 dB, marcas a cada 2,5 dB, números em todos os painéis |
| Perdas | chamar de "SNR increase over <referência> [dB]", não de "loss" sem referência |
| Nomes | grupos G1, G2, G3; configurações pelo número do grupo + letra, 1A–1H, 2A–2H, 3A–3H (nos três grupos: A, B 16-QAM e C, D QPSK com IoTh 10 dB; E, F 16-QAM e G, H QPSK com IoTh 20 dB; K = 8 antes de 12; QPSK de M = 256, 2C, 2D, 2G, 2H, 3C, 3D, 3G, 3H, só na [4] v5) (`LETRAS` de `mapa_cenarios_v4.py`); interferência como **IoTh** (interference over thermal), nunca IoT; TDLA30-5, TDLB100-400 etc. são **test conditions** (nunca "scenarios"; "propagation scenario" é o UMa NLOS do QuaDRiGa) |

## 3. Algoritmos (curvas de SER e pontos)

| Entidade | Cor | Marcador | Faixa (min–max) | Linha |
|---|---|---|---|---|
| LMMSE (float) | vermelho `#d62828` | `o` | preenchida, alpha 0,18 | mediana cheia, 1,6 pt |
| ZF (float) | cinza `#8a8983` | `s` | preenchida, alpha 0,18 | mediana cheia, 1,6 pt |
| BCD-MMSE iter 1 com a inversa em ponto fixo | amarelo forte `#eda100` (o mesmo da parte float das barras) | `v` | **só hachura `////`**, sem preenchimento, `hatch.linewidth` 0,45 | mediana cheia, 1,6 pt |
| BCD-MMSE iter 1 em float (referência da perda) | preto `INK_PRIMARY` | — | — | tracejada `(0, (3, 2))`, 0,8 pt |
| Bordas das faixas | a cor da série | — | — | 0,6 pt, alpha 0,8 |
| Alvo SER = 10⁻² | `INK_MUTED` | — | — | pontilhada, 0,6 pt |

A faixa do BCD-MMSE é hachurada porque se sobrepõe à do LMMSE: duas faixas preenchidas
gerariam uma cor de mistura.

**Amarelo forte = BCD-MMSE; degradê azul = aumento de SNR do formato** (decidido com a autora em
2026-11-02). As curvas do BCD-MMSE e a parte float das barras ficam em amarelo forte `#eda100` (lavanda
e cinza foram recusados); o degradê do
mapa (`mapa_cenarios_v4.py`, de `#cde2fb` a `#0d366b`) só aparece onde a cor mede quanto o
formato aumenta a SNR: o mapa e a parte do formato nas barras.

**Estudo de iterações (só nessa figura):** BCD-MMSE iter 1 a 4 usam a rampa do simulador,
`#eda100`, `#35bcd9`, `#2a78d6`, `#4a3aa7`, com marcadores `v`, `^`, `D`, `<`
(`BCD_ITERATION_RAMP` em `dbp_sim/plotting.py`). Nas outras figuras esses azuis têm outro
papel (seção 4), então a rampa não sai do estudo de iterações.

## 4. Grandezas derivadas (barras)

| Grandeza | Cor | Textura |
|---|---|---|
| Aumento de SNR da descentralização (BCD-MMSE float sobre LMMSE) | amarelo forte `#eda100` (escolha da autora em 2026-11-02; recusou cinza e lavanda) | cheia |
| Aumento de SNR do formato (BCD-MMSE no formato sobre BCD-MMSE float) | degradê do mapa (`DEGRADE` e `NORMA` de `mapa_cenarios_v4.py`), pela magnitude da parte | cheia |
| Valor que é só limite inferior (curva já abaixo de 10⁻² em −10 dB) | a cor da parte | hachura `////` branca; legenda só "LMMSE already below 10⁻²" |

- A parte do formato usa a mesma escala de cor do mapa de pior aumento de SNR: a mesma cor
  quer dizer o mesmo valor em dB nas duas figuras. Na legenda, a alça mostra três faixas do
  degradê. A descentralização fica em amarelo forte, que contrasta com todo o degradê azul.
- Títulos dos painéis e das figuras (barras, comparação de formatos, perfis): sem G1, G2, G3; só a modulação (se o grupo mistura) e
  `M = …, C = …, M_c = …` ($M_c = M/C$, tamanho da matriz invertida), não "16 × 16 circuit".
- Legenda: o item do limite inferior fica logo abaixo do item da parte que ele marca.
- Atributos das configurações (IoTh, K): caixas cinza `FAIXA #e4e3df` retas (sem cantos arredondados), justas ao texto (altura 0,6 da linha), como no mapa de perda; valores seguidos iguais numa caixa só, sem mudar a ordem; K não passa da divisa do IoTh.
- Barra empilhada: as partes somam; a segunda começa onde a primeira termina.
- Entre partes, contorno de 1 pt na cor do fundo.
- `////` tem dois usos, aceitos pela autora (ela não gostou dos pontos): faixa do BCD-MMSE
  nas curvas (linhas na cor da série, sem fundo) e limite inferior nas barras (linhas
  brancas sobre a cor da parte). Pelo fundo os dois não se confundem.

## 5. Categorias

| Categoria | Cores | Marcadores |
|---|---|---|
| IoTh | 10 dB `#2a78d6`, 20 dB `#eb6834` | — |
| K | — (sem cor) | 8 `o`, 12 `s` |
| Grupo | G1 `#2a78d6`, G2 `#eb6834`, G3 `#4a3aa7` | G1 `o`, G2 `s`, G3 `D` |
| Cenário | TDLA30-5 `#52514e`, TDLA30-75 `#35bcd9`, TDLA30-300 `#eb6834`, TDLC300-100 `#4a3aa7`, TDLB100-400 `#d64ad6` | `o`, `s`, `D`, `^`, `v` |
| Perfil de mobilidade (`figuras_perfis.py`) | preto `INK_PRIMARY`, sem borda (amarelo e rosa recusados), sobre o fundo no degradê do mapa: lento vazado, rápido cheio, sobre o fundo no degradê do mapa (`DEGRADE`/`NORMA`) | lento `o` vazado, rápido `o` cheio |
| Formato (série de pontos ou de custo) | rampa de um azul, do menor para o maior W: `#86b6ef`, `#3987e5`, `#256abf`, `#184f95`, `#0d366b` | `v`, `^`, `s`, `D`, `o` |

Uma figura usa no máximo uma categoria por cor. Se precisar de duas (por exemplo, grupo e
IoTh), uma vai na cor e a outra no marcador.

## 6. Faixas de perda (fundos e mapas)

| Faixa | Cor |
|---|---|
| até 0,1 dB | cinza claro `#e6e5e0` |
| de 0,1 a 3 dB | amarelo claro `#fde3a7` |
| acima de 3 dB | vermelho claro `#f4c6c6` |
| não chega a 10⁻² | `×` vermelho `#d03b3b` |

## 7. O que ainda está fora do padrão

Corrigir ao regenerar (junto com a passagem para o inglês):

| Onde | Desvio | Correção |
|---|---|---|
| `figuras_analise_grupos.py` | português, vírgula; negrito em títulos; ZF em rosa `#e87ba4` na figura de SNR necessária | inglês, ponto, sem negrito; ZF cinza `#8a8983` |
| `figuras_zonas.py` | português, vírgula; negrito nos nomes das zonas | inglês, ponto, sem negrito |
| `dbp_sim/plotting.py` (reprodução da Fig. 8 do Zhao) | BCD-MMSE iter 1 em verde `#0a7a30`, ZF magenta: segue as cores do artigo | decidir com a autora: manter só na validação do simulador ou trocar o verde |
| `dbp_sim/plotting.py` (estudo de iterações) | ZF rosa `#e87ba4` | ZF cinza `#8a8983`, se a figura entrar no texto |
