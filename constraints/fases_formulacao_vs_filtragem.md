# Fase de formulação vs. fase de filtragem — trilha de evidência

**Objetivo deste documento:** justificar, com citação literal ao artigo, por que o orçamento
temporal do módulo de inversão de matriz é **T_OFDM / N_PRB = 30,303 ns** e não
**T_OFDM / N_u = 2,525 ns**.

**Fonte da verdade:** Zhao, Li, Wang, Song, Chang, Shi, *"Efficient LMMSE Equalization for
Massive MIMO Systems Under Decentralized Baseband Processing Architecture"*, IEEE JSAC,
vol. 43, 2025. DOI 10.1109/JSAC.2025.3531524.

**Arquivo citado:**
`constraints/Efficient_LMMSE_Equalization_for_Massive_MIMO_Systems_Under_Decentralized_Baseband_Processing_Archit.md/paper.md`

> **Nota sobre as citações:** os excertos são reproduzidos com a formatação LaTeX
> normalizada (espaçamento e `\text{}` simplificados, marcadores de nota de rodapé
> omitidos). O **conteúdo** é literal — confira pelos números de linha.

**Escopo:** arquitetura DBP *daisy chain*, equalizador BCD-MMSE (Algoritmo 3, eq. 30).
Fora de escopo: sDR-MMSE, cDR-MMSE (arquitetura estrela) e a variante BCD-MMSE (LRD).

**Documento relacionado:** `constraints.csv` (mapeamento completo de restrições; ver NOTA 1,
NOTA 2, NOTA 14, NOTA 15 e NOTA 18).

---

## 1. Resumo do argumento

O equalizador LMMSE opera em dois tempos, **nomeados pelo próprio artigo**:

| Fase | O que faz | Depende de | Cadência por símbolo OFDM |
|---|---|---|---|
| **Formulação** (*formulation phase*) | calcula a matriz `W` — **contém a inversão** | canal `H` e covariância `R` | **N_PRB = 275** |
| **Filtragem** (*filtering phase*) | aplica a matriz: `ŝ = W·y` | sinal recebido `y` | **N_u = 3300** |

A razão entre as cadências é exatamente o número de subportadoras por PRB:

```
T_OFDM / N_PRB = 8,333333 µs / 275  = 30,303030 ns   ← formulação (nosso módulo)
T_OFDM / N_u   = 8,333333 µs / 3300 =  2,525253 ns   ← filtragem  (outro módulo)

30,303030 / 2,525253 = 12 = N_sc,PRB
```

**Motivo físico:** o canal é (por premissa do artigo) constante dentro de um PRB, mas o
*dado* não — cada uma das 12 subportadoras do PRB carrega um símbolo QAM diferente, com um
`y` diferente. Logo:

```
1 PRB  →  1 formulação de W  →  12 filtragens reusando o mesmo W
```

**Consequência de projeto:** dimensionar o inversor pelos 2,525 ns superdimensiona o módulo
em 12×.

---

## 2. Excertos — as duas fases existem e são nomeadas

### 2.1 Fase de formulação — `paper.md:616`

> "**1) Formulation phase:** Define $\mathbf{A}$ as the set of all matrices transmitted
> during the equalization matrix formulation phase for a decentralized scheme. For example,
> A includes $\{\mathbf{Q}_c \mathbf{H}_c, \{\mathbf{Q}_c \mathbf{n}_c^i\}_{i=1}^N\}_{c=1}^C$
> for DR-MMSE. The average fronthaul data rate during the formulation phase can be
> calculated using the following equation:"

`paper.md:619` — a equação:

$$R_{\mathrm{form}} = \frac{w \, S_{\mathbf{A}} \, N_{\mathrm{PRB}}}{T_{\mathrm{OFDM}}}$$

`paper.md:622` — a legenda:

> "where $w$ is the bit-width of each element in $\mathbf{A}$ (including both real and
> imaginary parts), $S_{\mathbf{A}}$ is the total number of real elements in A, and the
> numerator represents the total number of bits required to transfer A within one OFDM
> symbol."

### 2.2 Fase de filtragem — `paper.md:623` e `paper.md:628`

> "**2) Filtering phase:** The local processing results (e.g., $\{\mathbf{Q}_c\mathbf{y}_c\}_{c=1}^C$
> for DR-MMSE.) are collected to obtain [...] the final estimate. The average fronthaul data
> rate during the filtering phase can be calculated as"

`paper.md:631` — a equação:

$$R_{\mathrm{fil}} = \frac{w \, S_{\mathbf{s}} \, N_{\mathrm{u}}}{T_{\mathrm{OFDM}}}$$

### 2.3 Leitura

As duas fórmulas têm **estrutura idêntica** — mesmo `w`, mesmo `T_OFDM`, mesma forma. A única
diferença é o multiplicador: `N_PRB` na formulação, `N_u` na filtragem. É essa comparação lado
a lado que estabelece as duas cadências distintas.

> **Ressalva (mesma da NOTA 15 do CSV):** ambas as fórmulas medem **taxa de dados no
> fronthaul**, não tempo de computação. O artigo nunca escreve "a formulação deve ser
> *computada* 275 vezes por símbolo" — escreve que é *transferida* 275 vezes. A transposição
> transferência → computação é derivação nossa. É forçada (não se transmite um resultado de
> formulação que não foi calculado), mas deve ser enunciada como derivação na metodologia do TG.

---

## 3. Excerto — `N_u = 12 × N_PRB` e um canal diferente por PRB

`paper.md:614`:

> "we leverage channel correlation based on the physical resource block (PRB) concept outlined
> in the third-generation partnership project (3GPP) technical standards. A PRB is defined as
> a frequency-time stripe over which the wireless channel remains constant across all
> subcarriers. Within an OFDM symbol, the number of subcarriers in each PRB and the number of
> PRBs per symbol are specified as $N_{sc,PRB}$ and $N_{PRB}$, respectively. **Each symbol
> contains $N_u \triangleq N_{sc,PRB} \times N_{PRB}$ subcarriers (a resource element in OFDM
> system) to carry user data within a duration of $T_{OFDM}$. Each PRB corresponds to a
> different channel matrix in the baseband model in (1).**"

Duas informações decisivas nas frases em negrito:

1. `N_u = N_sc,PRB × N_PRB` → **o fator 12 entre os dois orçamentos é literalmente o
   `N_sc,PRB`**, não uma coincidência numérica.
2. *"Each PRB corresponds to a different channel matrix"* → `H` muda uma vez por PRB; como `W`
   depende de `H`, `W` muda uma vez por PRB. Este argumento **não depende do esquema** (DR ou
   BCD): vale para qualquer equalizador cujo `W` seja função de `H`.

> **Ressalva conceitual (NOTA 18 do CSV):** a frase *"A PRB is defined as a frequency-time
> stripe over which the wireless channel remains constant"* **não é** a definição 3GPP de PRB.
> PRB é unidade estrutural de alocação (12 subportadoras consecutivas; em NR definida no
> domínio da frequência, TS 38.211). Quem descreve a região onde o canal permanece
> aproximadamente constante é a **largura de banda de coerência `B_c`** e o **tempo de coerência
> `T_c`**, propriedades estatísticas do canal. O artigo usa o PRB como *proxy* da região de
> coerência — e meio que admite, ao escrever *"we leverage channel correlation based on the PRB
> concept"*. A premissa é **conservadora** (PRB ⊆ B_c), então os 30,303 ns nunca subestimam o
> requisito; e a relação numérica `N_u = 12 × N_PRB` se sustenta independentemente.

---

## 4. Excerto — os valores numéricos

`paper.md:640`:

> "For the numerical results, we set $N=192$, $r=8$, and $w=12$. The remaining system parameters
> are configured as follows **according to the worst case in 5G NR: $N_u=3300$, $N_{PRB}=275$,
> $N_{sc,PRB}=12$ and $T_{OFDM}=\frac{1}{120\,\mathrm{KHz}}$**."

Verificação de consistência interna: 275 × 12 = 3300. OK

Notas:
- `N_PRB = 275` é do próprio artigo, declarado como "pior caso em 5G NR". É o máximo absoluto
  de `N_RB` em NR — portanto conservador (ver NOTA 9 do CSV).
- `w = 12 bits` é a largura de palavra do **fronthaul**, **não** a precisão aritmética interna do
  inversor, que o artigo não especifica (ver NOTA 5 do CSV).

---

## 5. Excertos — filtragem é *aplicar* `W`, não recalcular

### 5.1 Definição geral — `paper.md:79`

> "The LMMSE estimate $\hat{\mathbf{s}}_{MMSE}$ is obtained by **applying the equalization
> matrix** $\mathbf{W}_{MMSE}$ to the received signal $\mathbf{y}$, i.e.,
> $\hat{\mathbf{s}}_{MMSE} = \mathbf{W}_{MMSE}\mathbf{y}$. Finally, the detector quantizes each
> entry of $\hat{\mathbf{s}}_{MMSE}$ to the nearest neighbor point in the constellation set
> $\mathcal{S}$."

### 5.2 No nosso caso específico — Algoritmo 3, `paper.md:430–434`

Bloco final do Algoritmo 3 (BCD-MMSE, daisy chain), transcrito do pseudocódigo LaTeX:

```
Equalizer filter:
    ŝ_BCD-MMSE ← 0;
    for c = 1 to C do
        ŝ_BCD-MMSE ← ŝ_BCD-MMSE + W_c · y_c;
    end for
```

Nenhuma inversão, nenhuma iteração — apenas `C` multiplicações matriz-vetor (`K×Mc` por `Mc×1`)
somadas ao longo do anel. **É este bloco que roda 3300 vezes por símbolo OFDM.**

**O módulo de filtragem, para efeito de fronteira de escopo** *(dimensionamento nosso, não do
artigo)*: `paper.md:383` estabelece `W_c ∈ ℂ^{K×Mc}` — "we deliberately partition the
equalization matrix $\mathbf{W}$ into block matrix as $\mathbf{W}=[\mathbf{W}_1,\ldots,\mathbf{W}_C]$
with $\mathbf{W}_c \in \mathbb{C}^{K \times M_c}$". Logo `W_c·y_c` é um array de
multiplicação-acumulação complexo de `K·Mc` MACs por DU por resource element (128 MACs na
config A: K=8, Mc=16), a cada 2,525 ns. Mais simples que o inversor, porém com cadência 12×
mais apertada. **Não é o módulo deste trabalho.**

---

## 6. Excertos — a eq. (30) pertence à formulação

### 6.1 Estrutura do Algoritmo 3 — `paper.md:422–429`

Corpo do algoritmo, imediatamente **antes** do bloco `Equalizer filter` citado acima:

```
BCD iterations:
    for l = 1 to T do
        for c = 1 to C do
            Update W_c^l via (30);
            Update A_c^l  via (28);
            Update b_{c,i}^l, i = 1,2,...,N via (29);
        end for
    end for
```

A separação é explícita no próprio pseudocódigo: a eq. (30) **produz** `W`; o bloco
`Equalizer filter` **consome** `W`.

### 6.2 A equação (30) — `paper.md:504`

$$\mathbf{W}_c^l=\Big(E_s(\mathbf{I}_K-\mathbf{A}_{c-1}^l+\mathbf{W}_c^{l-1}\mathbf{H}_c)\mathbf{H}_c^H-\tfrac{1}{N}\sum_{i=1}^{N}\big((\mathbf{b}_{c-1,i}^l-\mathbf{W}_c^{l-1}\mathbf{n}_c^i)(\mathbf{n}_c^i)^H\big)\Big)\times\Big(E_s\mathbf{H}_c\mathbf{H}_c^H+\tfrac{1}{N}\sum_{i=1}^{N}\mathbf{n}_c^i(\mathbf{n}_c^i)^H\Big)^{-1}$$

**O módulo alvo é o fator direito:**

$$\Big(E_s\mathbf{H}_c\mathbf{H}_c^H+\tfrac{1}{N}\sum_{i=1}^{N}\mathbf{n}_c^i(\mathbf{n}_c^i)^H\Big)^{-1} \in \mathbb{C}^{M_c \times M_c}$$

Hermitiano definido positivo, complexo, dimensão `Mc × Mc` (8, 16 ou 32 conforme a config).

**Evidência textual da NOTA 2:** o fator invertido **não carrega o índice de iteração `l`**.
Ele depende apenas de `Hc` e `{nc^i}`, ambos locais e constantes durante toda a execução do BCD.
Portanto: (a) `T` não multiplica a inversão; (b) as `C` instâncias são paralelas entre DUs;
(c) a serialização Gauss-Seidel do anel afeta a propagação de `A_c` e `b_{c,i}`, não o inversor.

`paper.md:447` confirma a leitura de localidade:

> "the $c$-th DU receives the communication variables $\mathbf{A}_{c-1}^l$ and
> $\{\mathbf{b}_{c-1,i}^l\}_{i=1}^N$ from the previous DU. Then the local equalization matrix
> $\mathbf{W}_c^l$ is updated by as in (30) [...] **Except for the information received from the
> previous DU, all other terms in (30) can be computed locally.**"

---

## 7. Excertos — por que o artigo separa as fases (motivação de fundo)

`paper.md:61`:

> "the CSI is considered almost constant across several contiguous symbols [15], which **enables
> the reuse of the equalization matrix**. Consequently, it is more cost-effective to compute the
> equalization matrix and reuse it, rather than estimating symbols directly for each instance.
> Therefore, we focus on obtaining an equalization matrix instead of directly estimating symbols."

`paper.md:31` — o mesmo argumento na revisão da literatura:

> "the equalization matrix can be reused across multiple coherence blocks of channels. In
> contrast, the symbol estimation algorithms mentioned above must be performed for each channel,
> resulting in high computational complexity and communication bandwidth."

`paper.md:561` — a quantificação (Seção V-B):

> "We assume that the channel and noise covariance remain static across $N_{coh}$ contiguous
> symbols. This means that the equalization matrix and covariance estimation can be reused for
> different symbols, although they will change with every coherence block. Thus **the data
> required for computing the equalization matrix is transferred only once for $N_{coh}$ symbols,
> while the received signal y must be transferred for each symbol.**"

**Leitura:** este é o mesmo desequilíbrio da Seção 1 deste documento, mas visto no eixo do
**tempo** em vez do da **frequência** — formulação é rara, filtragem é frequente. É a tese
econômica que sustenta o artigo inteiro: vale a pena pagar caro por `W` porque `W` é reusado
muitas vezes.

---

## 8. Índice de citações

| Afirmação | Linha em `paper.md` |
|---|---|
| Existem duas fases nomeadas (formulação / filtragem) | 616, 623 |
| `R_form` escala com `N_PRB` | 619 |
| `R_fil` escala com `N_u` | 631 |
| `N_u = N_sc,PRB × N_PRB`; cada PRB tem um `H` diferente | 614 |
| Valores: `N_PRB=275`, `N_u=3300`, `N_sc,PRB=12`, `T_OFDM=1/120 kHz`, `w=12`, `N=192` | 640 |
| Filtragem = aplicar `W` ao sinal (`ŝ = W·y`) | 79 |
| Filtragem no daisy chain = `ŝ = Σ_c W_c·y_c`, sem inversão | 430–434 |
| Eq. (30) está no laço `BCD iterations`, antes da filtragem | 422–429 |
| Eq. (30) na íntegra; fator invertido **sem** índice `l` | 504 |
| Termos da eq. (30) são locais, exceto `A_{c-1}` e `b_{c-1,i}` | 447 |
| `W_c ∈ ℂ^{K×Mc}` (dimensiona o módulo de filtragem) | 383 |
| Motivação: `W` é reusável entre símbolos | 31, 61, 561 |
| Conta de banda dividida nos três blocos do Algoritmo 3 | 571 |
| Definição de `A_c^l ∈ ℂ^{K×K}` e `b_{c,i}^l ∈ ℂ^{K×1}` (variáveis de interação) | 438 |
| Topologia daisy chain: sem CU, enlaces unidirecionais, anel, um só DU no decodificador | 87 |
| Fechamento do anel: `A_0^l = A_C^{l-1}` (nota de rodapé 6) | 450 |

---

## 9. Pontos em aberto ligados a este documento

1. **Transferência ≠ computação** (Seção 2.3). Derivação nossa; enunciar como tal no TG.
2. **PRB como proxy de `B_c`** (Seção 3). Verificar contra o espalhamento de atraso do QuaDRiGa
   na configuração do artigo (setor de 120°, raio 50–100 m): se `B_c > 1,44 MHz` (= 12 × 120 kHz),
   a premissa vira resultado verificado. Se `B_c` abranger `G` PRBs consecutivos, `W` é
   recalculado 1× a cada `G` PRBs e o orçamento **afrouxa por fator `G`**.
3. **`N_coh` sem valor numérico** no artigo — relaxaria ainda mais o orçamento no eixo do tempo,
   mas não é quantificável com o que está publicado.

---

## 10. Confirmação independente na conta de fronthaul (`paper.md:571`)

Esta é a evidência mais limpa de que o mapeamento fases ↔ blocos do Algoritmo 3 é o do
próprio artigo, e não uma leitura nossa.

> "The average data transfer size of the proposed BCD-MMSE method is
> `C(4K² + 2NK)/N_coh + 2TCK(N+K)/N_coh + 2CK`,
> where **the three terms are induced by preprocessing, `T` iterations for computing
> equalization matrix, and symbol estimation, respectively**."

Repare em quais termos são divididos por `N_coh`:

| Termo | Bloco do Algoritmo 3 | ÷ `N_coh`? | Leitura |
|---|---|---|---|
| `C(4K² + 2NK)/N_coh` | `Preprocessing` (`:414-421`) | **sim** | pago 1× por bloco de coerência → **formulação** |
| `2TCK(N+K)/N_coh` | `BCD iterations` (`:422-429`) | **sim** | pago 1× por bloco de coerência → **formulação** |
| `2CK` | *symbol estimation* (`:430-434`) | **não** | pago a cada símbolo → **filtragem** |

O artigo amortiza os dois primeiros por `N_coh` e o terceiro não. É exatamente a
assimetria entre as duas fases aparecendo na própria contabilidade de banda — coerente
com `:561` (Seção 7) e com a razão 12 da Seção 1.

**Alcance desta evidência.** `:571` estabelece a estrutura *amortizada* (formulação) vs.
*não-amortizada* (filtragem), e **apenas isso**. A **cadência** de cada fase — por PRB
para a formulação, por RE para a filtragem — vem de fonte distinta: `:619`, onde `R_form`
multiplica por `N_PRB`, e `:631`, onde `R_fil` multiplica por `N_u`. São duas evidências
independentes que convergem; não apresentar `:571` como origem da cadência.

---

## 11. Diagramas

O conteúdo deste documento está desenhado em PlantUML em `diagramas/`
(ver `diagramas/README.md` para a ordem de leitura e as convenções):

| Arquivo | Corresponde a |
|---|---|
| `diagramas/fases.puml` | Seções 1, 2, 3, 4 e 7 deste documento |
| `diagramas/algoritmo3.puml` | Seções 5 e 6 — pseudocódigo transcrito fielmente |
| `diagramas/algoritmo3_hardware.puml` | Seção 6 — a reordenação (derivação nossa) da eq. (30) |
| `diagramas/anel_formulacao.puml` | O percurso hop a hop da formulação no anel |
| `diagramas/anel_filtragem.puml` | Seção 5 — o percurso da filtragem no anel |
| `diagramas/anel_pipeline.puml` | Ponto em aberto 1 — orçamento de vazão vs. latência |
| `diagramas/modelo_ruido.puml` | de onde vem a matriz a inverter — ver `modelo_ruido_e_hipoteses.md` §10 |

O roteiro de redação do texto do TG, com as decisões de atribuição, está em `notas_redacao.md`.

---

## 12. Documento irmão — o modelo de ruído

Este documento parte de premissas que **não** justifica: que existe uma matriz `W` a formular,
que ela é cara, e que a matriz invertida na eq. (30) é cheia e hermitiana definida positiva.

De onde essas premissas vêm está em **`modelo_ruido_e_hipoteses.md`**:

| Seção de lá | Cobre |
|---|---|
| 2, 3 | decodificador de notação e inventário dos objetos (`n`, `n_c`, `n^i`, `R`, `R_cc`, `R̂_cc`) |
| 4 | a construção de `R` — o que é definição, o que é teorema, o que é hipótese |
| 5 | as hipóteses H1–H9, com as justificativas das notas de rodapé (`:815`–`:824`) |
| 6 | de onde vem `β`, e por que ele nunca entra no datapath |
| 7 | a armadilha da nota 5: o artigo funde `R̂` e `R` a partir de `:123` |
| 8, 9 | os inputs do Algoritmo 3 e a anatomia do bloco `Preprocessing` |
| 10 | o fluxo completo, da hipótese ao silício |

Em particular, a **nota de rodapé 3** (`paper.md:819`) é a justificativa mais forte para a
existência deste TG: com ruído branco, bastaria uma única inversão `K × K` — não haveria
inversor `Mc × Mc` para projetar.

Os diagramas usam as mesmas convenções `[ARTIGO :NNN]` / `[NOSSO]` e a mesma ressalva
de transliteração LaTeX → ASCII declarada no topo deste arquivo.
