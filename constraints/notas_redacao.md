# Notas de redação — capítulo do ruído colorido até `G_c`

Documento de **trabalho**, não de evidência. Os outros arquivos registram *o que o artigo diz*;
este registra *como apresentar isso no texto do TG* — ordem dos tópicos, decisões de atribuição
e correções pendentes.

**Fonte da verdade:** `Efficient_LMMSE_Equalization_..._Archit.md/paper.md`
(Zhao et al., IEEE JSAC vol. 43, 2025 — DOI 10.1109/JSAC.2025.3531524).

**Documentos irmãos:**

| Arquivo | Cobre |
|---|---|
| `modelo_ruido_e_hipoteses.md` | a trilha de evidência: hipóteses H1–H9, excertos, índice de citações |
| `fases_formulacao_vs_filtragem.md` | formulação vs. filtragem, orçamentos de tempo |
| `constraints.csv` | o mapa de restrições e as 25 notas |
| `diagramas/modelo_ruido.puml` | este mesmo caminho, em forma de grafo |

---

## 1. Estado do texto (atualizado em 2026-09-08)

**Já escrito**, até o fim da definição de `R`:

1. Eq. (5) — decomposição `y = Hs + H̄s̄ + n̄`, com figura TikZ das dimensões
2. Definição de `H̄`, `s̄`, `n̄`, `σ²`
3. Parágrafo sobre covariância e esperança matemática; `Cov(x) = E[xx^H]` para média nula
4. As hipóteses sobre `s̄` e `n̄`, com figura TikZ das matrizes `βI_r` e `σ²I`
5. As duas identidades (transformação linear; soma de independentes)
6. A derivação de `R = βH̄H̄^H + σ²I`
7. Leitura do resultado: `σ²I` diagonal vs. `βH̄H̄^H` cheia; correlação criada pelo canal
8. Consequência para a DBP: `R` não é bloco-diagonal; `R_mn` exigiria troca entre DUs

**Alvo:** o fator direito da eq. (30),
`( E_s H_c H_c^H + (1/N) Σ_i n_c^i (n_c^i)^H )^{-1}`.

---

## 2. Terminologia — três objetos que não podem se confundir

Esta distinção é o eixo do capítulo. Errar aqui apaga o argumento central do artigo.

| Objeto | O que é | Palavra correta | Onde aparece |
|---|---|---|---|
| `R̂` vs. `R` | amostras finitas vs. esperança | **estimativa** | eq. (6), `:119` |
| `R_B` vs. `R` | blocos cruzados zerados à força | **aproximação** (palavra do artigo, `:131`) | eq. (7) |
| `R̂_cc` | o bloco `(c,c)` da estimativa | **nem uma nem outra** — é o bloco exato | eq. (30), `:504` |

**`R̂_cc` na eq. (30) não aproxima nada.** O BCD é exato — `[ARTIGO :375]`:

> "the DR-based equalizers are only **suboptimal** solutions to the original LMMSE problem (2).
> Therefore, we aim to design an **optimal** decentralized equalizer for the daisy chain
> architecture by reconsidering problem (2)."

E `[ARTIGO :39]`, na lista de contribuições: "To obtain an **optimal** decentralized equalizer,
we reshape the original optimization problem of LMMSE".

Os blocos cruzados não são descartados: reaparecem comprimidos em `A_c` e `b_{c,i}`.

**A mesma `R̂_cc` aparece duas vezes com estatutos diferentes:** dentro da eq. (7) ela compõe
uma aproximação; dentro da eq. (30) não.

---

## 3. O roteiro — seis tópicos

### T1 — `R` é uma fórmula que ninguém consegue avaliar

O **pivô** do capítulo: acima dele, modelagem; abaixo, implementação. Duas razões independentes:

- `H̄` é determinística mas **desconhecida**. A BS não estima o canal dos interferentes nem
  conhece `β`. (Aproveitar que "determinística" já foi plantado no texto atual.)
- `E[·]` é média sobre infinitas realizações.

Daí a estimativa amostral, eq. (6) `[ARTIGO :119]`:
`R̂ = (1/N) Σ_i n^i (n^i)^H`, com `N` REs de piloto e `N ≫ K` `[ARTIGO :123]`.

Incluir o **argumento de posto**: cada `n^i(n^i)^H` tem posto 1, logo são necessárias ao menos
tantas amostras quanto a dimensão da matriz. É o que garante, em T6, que a matriz a inverter
não é singular.

Duas notas de rodapé:
- `[ARTIGO :821]` (nota 4) — a covariância é constante num intervalo largo de frequência, logo
  as amostras podem vir da **frequência**. Sem isso o leitor imagina 192 símbolos de latência.
- `[ARTIGO :821]` (nota 5) — o artigo **abandona o chapéu** a partir de `:123`: "we make no
  distinction between `R̂` and `R` in the rest of this paper". Avisar, senão as equações citadas
  adiante confundem.

### T2 — O particionamento: o que cada DU alcança

| Conteúdo | Linha |
|---|---|
| `M` antenas em `C` clusters de `Mc` | 85 |
| `y = [y_1^T,...,y_C^T]^T`, idem `H` e `n` | 96 |
| `H_c ∈ ℂ^{Mc×K}`, `n_c`; proibido trocar entre DUs | 104 |
| `n^i` particionado em `{n_c^i}`; `R_mn = E[n_m n_n^H]` | 125 |
| trocar amostras custaria `M × N` | 130 |

Conclusão: **cada DU calcula `R̂_cc` sozinho; nenhum DU calcula `R̂_mn` com `m ≠ n`.**
Pôr o número: `M × N` = 128 × 192 = 24 576 complexos por bloco de coerência.

### T3 — A bifurcação  (NÃO PODE SAIR DO TEXTO)

Eixo do capítulo, e estrutura do próprio artigo (Seção II-B-3 vs. Seção IV).

```
              blocos cruzados R̂_mn são inalcançáveis
                            |
              +-------------+-------------+
              v                           v
        DESCARTAR                   MANTER, COMPRIMIDOS
   R_B = blkdiag(R_11,...,R_CC)     problema (2) reformulado
   eq. (7) -- BDAC-MMSE             BCD -- eq. (30)
   :131, :135-136                   :375, :379
              |                           |
    barato, forma fechada,        iterativo, ÓTIMO
    SUBÓTIMO (:375)               (:39, :375)
              |                           |
              +--> serve de PONTO INICIAL +
                   (:583)
```

Os dois caminhos não competem: `[ARTIGO :583]` — o BDAC-MMSE "serves as the initial point for
the BCD-based algorithms". Um inicializa o outro.

**Armadilha:** é tentador escrever que a DBP "aproxima `R` como bloco-diagonal". Isso vale para
a linha de base, **não** para o método do artigo. Sem este tópico, o leitor não distingue a
linha de base do método — e é essa distinção que justifica a complexidade do módulo do TG.

### T4 — A formulação BCD

| Conteúdo | Linha |
|---|---|
| DR é subótimo; buscar o ótimo reconsiderando (2) | 375 |
| problema (24) — MSE com as `N` amostras | 379 |
| partição `W = [W_1,...,W_C]`, `W_c ∈ ℂ^{K×Mc}` | 383 |
| problema (25) — com `Σ_{j≠c}` explícito | 388 |
| BCD/Gauss-Seidel; `W_c` como redução de dimensionalidade | 392 |
| o que precisa vir dos outros DUs | 398 |
| eq. (27) — o subproblema por bloco | 402 |

Vale uma frase sobre `[ARTIGO :383]`: "the objective function has only one random variable `s`,
and the other variables are deterministic". As amostras `n^i` entram como vetores armazenados,
não como variável aleatória — é por isso que o problema (24) tem `(1/N)Σ_i` em vez de uma
esperança sobre o ruído.

### T5 — Da eq. (26) à eq. (30)

| Conteúdo | Linha |
|---|---|
| eq. (26) — solução ideal, com `Σ_{j≠c}` explícito | 454 |
| `A_c^l ∈ ℂ^{K×K}`, `b_{c,i}^l ∈ ℂ^{K×1}` — interaction variables | 438 |
| eqs. (28)/(29) — atualização recursiva | 442-443 |
| "local equalization matrices act as local compression matrices"; o hand-off no anel | 447 |
| eq. (30) | 504 |

O passo conceitual: `Σ_{j≠c} W_j H_j = A_{c-1} − W_c^{l-1} H_c`. Cada DU carrega o **total** e
subtrai a própria parcela desatualizada. É isso que permite trafegar `K × K` em vez de `Mc × K`,
e é onde os blocos cruzados sobrevivem — comprimidos.

### T6 — O fator a inverter

`G_c = E_s H_c H_c^H + R̂_cc`, fator direito da eq. (30).

Fechar identificando-o como a **covariância do sinal recebido local**, reusando as duas
identidades do texto atual com `A = H_c` e `z = s`:

```
E[y_c y_c^H] = H_c E[s s^H] H_c^H + E[n_c n_c^H] = E_s H_c H_c^H + R_cc
```

Daí saem, de graça: hermitiana, semidefinida positiva, e **definida positiva** porque `R̂_cc`
tem posto completo quando `N ≫ Mc` — enquanto `E_s H_c H_c^H` sozinha é **singular**
(posto ≤ `K < Mc`).

É aqui que o TG começa: essa é a matriz que o módulo vai fatorar.

**Pagamento do investimento:** as duas identidades enunciadas uma vez são usadas duas vezes
cada. O leitor que reconhecer o padrão entende `G_c` de graça.

---

## 4. Decisões de atribuição

O que é do artigo e o que é acréscimo nosso. Cada item aqui precisa de nota de rodapé no TG.

### 4.1 `E[s̄ s̄^H] = β I_r` — hipótese implícita, mas **forçada**

Busca exaustiva: `s̄` aparece em `:109` e `:113` apenas (a terceira ocorrência, `:680`, é
`s̄_MMSE`, outro objeto). `β` aparece em `:113`, `:473`, `:577`, sempre glosado como "the power
of interference signals". **O artigo nunca enuncia a estatística de `s̄`.**

Mas a hipótese não é escolha: dado o `R` publicado, é a **única** possível. Seja
`Σ = E[s̄s̄^H]`; de `H̄ Σ H̄^H = β H̄ H̄^H` vem `H̄(Σ − βI)H̄^H = 0`, e como `H̄` é `M × r` com
`M = 128 ≫ r = 8` (posto-coluna cheio, genericamente), multiplicar por uma inversa à esquerda
dá `Σ = β I_r`.

**Nota de rodapé sugerida:**
> O artigo de referência não enuncia a estatística de `s̄`, apresentando diretamente a forma de
> `R`. A hipótese adotada é, contudo, a única compatível com essa forma, dado que `H̄` possui
> posto-coluna completo; explicitá-la torna a derivação autocontida.

### 4.2 `E[s s^H] = E_s I_K` — mesmo status

Também nunca enunciada, mas **usada numa derivação**: a eq. (35) do Apêndice A `[ARTIGO :653]`
escreve `E_MMSE = E_s I − E_s H^H(H H^H + (1/E_s)R)^{-1} H`. A matriz de MSE padrão é
`E = R_s − R_s H^H(H R_s H^H + R)^{-1} H R_s`; substituindo `R_s = E_s I_K` cai exatamente
na eq. (35). Com qualquer outro `R_s`, não cairia.

Explicitar junto com a de `β`, pelo mesmo motivo e com nota análoga.

### 4.3 `H̄_c` — notação que não existe no artigo

Busca exaustiva: `H̄` sempre aparece como `ℂ^{M×r}` (`:113`, `:473`, `:577`). **O artigo nunca
particiona `H̄` por cluster.** Se o texto precisar da estrutura de `R_cc`, introduzir:

> Seja `H̄_c ∈ ℂ^{Mc×r}` o bloco de linhas de `H̄` correspondente às antenas do cluster `c`.
> Então `R_cc = β H̄_c H̄_c^H + σ² I_{Mc}`.

Marcar como notação nossa.

Consequência a não transportar sem cuidado: o posto da parte de interferência é `r = 8` numa
matriz `128 × 128` (muito baixo, é o que a variante LRD explora, `:473`), mas por bloco é
`min(r, Mc)` — que em config B (`Mc = 8`) é **cheio**. A característica "quase posto baixo" é
global, não do bloco.

### 4.4 `G_c` como covariância do sinal recebido — leitura nossa

O artigo não nomeia `G_c` nem deriva a eq. (26) por esse caminho (deriva pelo MSE, `:379-383`).
Registrado como NOTA 25 do `constraints.csv` e nas seções 10.2 e 10.3 do
`modelo_ruido_e_hipoteses.md`.

---

## 5. Tensões e deslizes do artigo — não reproduzir

### 5.1 Modelo analítico vs. modelo de simulação

`:113` define `s̄ ∈ 𝒮^{r×1}`, e `𝒮` é o conjunto de **constelação** (`:60`, e.g. 16-QAM), ou seja
discreto. Mas `:577` diz que "the distribution of the colored noise follows a **complex Gaussian
distribution**, denoted as `CN(0, βH̄H̄^H + σ²I)`". `H̄s̄ + n̄` com `s̄` de 16-QAM **não é gaussiano**.

As **covariâncias coincidem exatamente** (para QAM de média nula e energia média `β`, com
símbolos independentes, `E[s̄s̄^H] = βI_r` sem aproximação), e o LMMSE é método de segunda
ordem — depende de `R` e de mais nada da distribuição. Inofensivo para o projeto.

**Mas não para o texto:** não afirmar que o ruído colorido é gaussiano apoiando-se em `:577`
enquanto se deriva de `s̄ ∈ 𝒮^{r×1}`. Dizer apenas o que se precisa: que a covariância é
`βH̄H̄^H + σ²I`. A gaussianidade não entra na derivação nem no hardware.

### 5.2 `:60` chama `n` de "white"

> "`n ~ CN(0, R)` denotes the additional **white** Gaussian noise (AWGN) with `R ≜ E[nn^H]`"

Chama `n` de branco enquanto `R` é genérica — e o artigo inteiro existe porque `R` não é branca.
**Ao citar `:60`, citar só a parte da definição de `R`.**

### 5.3 Interferentes co-localizados na simulação

`:577` coloca os UEs não-alvo segundo a mesma distribuição espacial dos alvos (setor de 120°,
raio 50–100 m). Interferentes próximos chegam fortes — coerente com os IoT altos varridos
(até 20 dB, `:593`), e reforça dimensionar o ponto fixo no pior caso. Se for preciso ser
rigorosa: dizer "usuários de células vizinhas" na motivação e notar em rodapé a posição
adotada na avaliação numérica.

---

## 6. Correções já identificadas no texto

| Onde | Erro | Correção |
|---|---|---|
| definição de `H̄` | "as respectivas `r` **antenas interferentes das estações** situadas em células vizinhas" | são **UEs**, não estações. `[ARTIGO :113]` "r non-target UEs"; `:52` "each with a single antenna" |
| parágrafo de covariância | "Para um **valor** aleatório" | "Para um **vetor** aleatório" |
| identidade da soma | "duas **variáveis** aleatórias `u` e `v`" | "dois **vetores** aleatórios" |
| fim do parágrafo das identidades | ponto duplicado | -- |
| legenda da fig. 1 | "dimensões das matrizes **do sistema**" | a figura mostra só as grandezas de interferência |
| leitura de `R` | "essa parcela **pode** apresentar elementos fora da diagonal" | genericamente **apresenta** |

Contexto do erro dos UEs: "células vizinhas" está certo e vem de `[ARTIGO :105]`
("non-target UEs in neighboring cells"). O que escorregou foi atribuir a transmissão às
*estações* dessas células em vez dos *usuários* delas. Se fossem as estações, seria
interferência BS→BS, que não bate com o modelo `H̄s̄` com `s̄` numa constelação de dados.

Confirmação de que é uplink — `[ARTIGO :52]`:
> "**1) Uplink System Model:** Consider an **uplink** massive MIMO system where `K` target UEs,
> each with a single antenna, **transmit data to a BS** equipped with `M` antennas, where `M ≫ K`."

---

## 7. Dependências a conferir antes de T6

1. **A eq. (3)** — `W_MMSE = (H^H R^{-1} H + (1/E_s)I)^{-1} H^H R^{-1}` `[ARTIGO :75]`. É onde
   `R^{-1}` aparece; sem ela o leitor não sabe por que `R` importa. Se não estiver no texto,
   entra antes de T1.
2. **`E_s`** `[ARTIGO :79]` e a hipótese `E[ss^H] = E_s I_K` (Seção 4.2 acima).
3. **A partição DBP** (`:85`, `:96`, `:104`) — o texto atual já menciona clusters ao falar de
   `R_mn`, mas a partição formal precisa vir antes.
