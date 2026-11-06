# Modelo de ruído, covariância e hipóteses do artigo — trilha de evidência

**Fonte da verdade:** `Efficient_LMMSE_Equalization_..._Archit.md/paper.md`
(Zhao et al., *Efficient LMMSE Equalization for Massive MIMO Systems Under Decentralized
Baseband Processing Architecture*, IEEE JSAC vol. 43, 2025 — DOI 10.1109/JSAC.2025.3531524).

**Escopo:** arquitetura *daisy chain*, equalizador BCD-MMSE (Algoritmo 3, eq. 30).
Fora de escopo: estrela (sDR/cDR-MMSE) e a variante BCD-MMSE (LRD).

**Convenções deste documento:**

- `[ARTIGO :NNN]` — afirmação do artigo, com o número da linha em `paper.md`.
- `[NOSSO]` — derivação nossa. **Não** está no artigo; precisa ser apresentada como tal na defesa.

**Nota sobre as citações:** os excertos são reproduzidos com a formatação LaTeX normalizada
(espaçamento e `\text{}` simplificados, marcadores de nota de rodapé omitidos). O **conteúdo**
é literal — confira pelos números de linha. Mesma ressalva do `fases_formulacao_vs_filtragem.md`.

**Documentos irmãos** (este arquivo não repete o que está neles):

| Arquivo | Cobre |
|---|---|
| `constraints.csv` | o mapa de restrições — grade de parâmetros, orçamentos de tempo, notas |
| `fases_formulacao_vs_filtragem.md` | a divisão formulação/filtragem, o fator 12, a conta de banda de `:571` |
| `diagramas/*.puml` | os mesmos conteúdos em forma visual (fases, Algoritmo 3, percurso do anel) |
| `notas_redacao.md` | documento de **trabalho**: roteiro T1–T6 do texto do TG, atribuições e correções |

---

## Índice

1. Como usar este documento
2. Decodificador de notação
3. Inventário de objetos em três camadas
4. A construção de `R` — definição, identidades, resultado
5. As hipóteses do artigo (H1 a H9)
6. De onde vem `β`
7. A armadilha da nota de rodapé 5 — o artigo funde `R̂` e `R`
8. Os inputs do Algoritmo 3
9. O bloco `Preprocessing` — a eq. (7) e a semeadura de `A` e `b`
10. O fluxo completo — da hipótese ao silício
11. Índice de citações
12. Descobertas desta sessão que afetam o `constraints.csv`
13. Pontos em aberto

---

## 1. Como usar este documento

Ele responde a uma pergunta: **por que a matriz que o nosso módulo inverte é cheia, mal
condicionada e de dimensão `Mc × Mc`?**

A resposta é uma cadeia causal que começa em hipóteses de modelagem e termina no datapath.
As Seções 2 e 3 são referência de consulta (o que cada símbolo significa). As Seções 4 a 7
são o argumento. As Seções 8 e 9 descem para o Algoritmo 3. A Seção 10 é o resumo visual.

**A fronteira mais importante do documento** está na Seção 10: acima dela, teoria e motivação;
abaixo, o que vira silício. Só um objeto atravessa — `R̂_cc`.

---

## 2. Decodificador de notação

O artigo usa marcas diacríticas com significado fixo. Fixando isto, quase toda a confusão
de leitura se resolve:

| Marca | Significa | Exemplos |
|---|---|---|
| **barra** `¯` | lado **não-alvo** (interferentes), ou componente primitiva do ruído | `H̄`, `s̄`, `n̄` |
| sem marca | o **total** | `H`, `s`, `n` |
| **subscrito `c`** | fatia **espacial** — o pedaço pertencente ao cluster/DU `c` | `n_c`, `H_c`, `y_c`, `W_c` |
| **sobrescrito `i`** | amostra **temporal/frequencial** — o `i`-ésimo RE de piloto | `n^i` |
| **sobrescrito `l`** | índice de **iteração BCD** | `W_c^l`, `A_c^l`, `b_{c,i}^l` |
| **chapéu** `^` | **estimado a partir de dados**, não o valor verdadeiro | `R̂`, `R̂_cc`, `ŝ` |
| `E[·]` | teórico — média sobre infinitas realizações | `R = E[n n^H]` |

Os eixos espacial (`c`) e amostral (`i`) são **independentes**, e é por isso que `n_c^i`
carrega os dois:

```
                     amostras de piloto (eixo i)
                  i=1     i=2     ...    i=192
               ┌───────┬───────┬──────┬────────┐
   clusters    │ n_1^1 │ n_1^2 │ ...  │n_1^192 │  <- tudo isto vive no DU 1
   (eixo c)    ├───────┼───────┼──────┼────────┤
               │ n_2^1 │ n_2^2 │ ...  │n_2^192 │  <- e isto no DU 2
               ├───────┼───────┼──────┼────────┤
               │  ...                          │
               └───────┴───────┴──────┴────────┘
                   └── n^i é uma COLUNA: vetor M x 1 espalhado por todos os DUs.
                       Nenhum DU sozinho enxerga um n^i inteiro.
```

> **Colisão de índices a evitar.** Ao falar de uma antena individual (por exemplo, a entrada
> `(a,b)` de uma matriz de covariância), NÃO use o subscrito `c` — no artigo ele significa
> cluster, não antena. Use letras diferentes (`a`, `b`) e diga explicitamente que são antenas.

---

## 3. Inventário de objetos em três camadas

### 3.1 Camada 1 — os ruídos (vetores aleatórios)

Em ordem de construção, do primitivo ao derivado:

| # | Símbolo | O que é | Dimensão | Linha |
|---|---|---|---|---|
| 1 | `s̄` | símbolos transmitidos pelos `r` UEs não-alvo | `r × 1` | 113 |
| 1 | `n̄` | AWGN térmico de fundo | `M × 1` | 113 |
| 2 | `H̄ s̄` | a interferência **como chega às antenas** | `M × 1` | 109 |
| 3 | `n = H̄s̄ + n̄` | **ruído colorido total** — é o `n` da eq. (1) | `M × 1` | 56, 109 |
| 4 | `n_c` | fatia de `n` visível ao DU `c` | `Mc × 1` | 104 |
| 5 | `n^i` | uma **amostra** de `n`, colhida no RE de piloto `i` | `M × 1` | 123 |
| 6 | `n_c^i` | fatia `c` da amostra `i` — **o que o DU realmente armazena** | `Mc × 1` | 125 |

Os itens marcados `1` são hipóteses de modelagem. Do `2` em diante, tudo é consequência.

### 3.2 Camada 2 — as covariâncias teóricas (levam `E[·]`)

| Símbolo | É a covariância de | Estrutura | Linha |
|---|---|---|---|
| `σ² I` | `n̄` | diagonal, posto `M` | 113 |
| `β H̄ H̄^H` | `H̄ s̄` | **cheia**, posto `r` (singular) | 113 |
| `R = β H̄H̄^H + σ²I` | `n` | cheia, posto `M` | 60, 113 |
| `R_cc` | `n_c` | hermitiana definida positiva | 125 |
| `R_mn`, `m ≠ n` | *covariância cruzada* entre `n_m` e `n_n` | **não é matriz de covariância** | 125 |
| `R_B = blkdiag(R_11,...,R_CC)` | de ninguém — é **aproximação forçada** de `R` | bloco-diagonal | 131 |

Duas armadilhas nesta camada:

- **`R_mn` com `m ≠ n` não é covariância.** É covariância cruzada: não é hermitiana, não é
  definida positiva, e nunca é invertida. Só os blocos da diagonal `R_cc` são covariâncias
  de verdade — e são os únicos que um DU consegue calcular sozinho.
- **`R_B` não é a covariância de nada.** É `R` com os blocos fora da diagonal zerados à força.
  Existe apenas para viabilizar a eq. (7), que é o chute inicial. O BCD existe justamente
  para corrigir essa aproximação.

### 3.3 Camada 3 — as estimativas (levam chapéu) — o que o hardware vê

| Símbolo | Estima | Como | Linha |
|---|---|---|---|
| `R̂ = (1/N) Σ_i n^i (n^i)^H` | `R` | média de `N = 192` amostras | 119 |
| `R̂_cc = (1/N) Σ_i n_c^i (n_c^i)^H` | `R_cc` | idem, apenas a fatia local do DU `c` | 119 + 125 |

**`R̂_cc` é o único objeto desta lista inteira que entra no datapath.**

### 3.4 Por que a ordem do artigo confunde

A ordem lógica (construção) e a ordem de apresentação **não coincidem**:

```
ordem lógica:     s̄, n̄  ->  n  ->  R  ->  R_cc  ->  R̂_cc
ordem do artigo:  R (:60)  ->  n aberto (:109)  ->  R̂ (:119)  ->  blocos (:125)  ->  R_B (:131)
```

O artigo apresenta `R` **antes** de dizer o que há dentro dela: em `:60` escreve apenas
`R ≜ E[n n^H]` e segue; cinquenta linhas depois, em `:109`, abre o `n`. É praxe em artigo
(modelo geral primeiro, caso concreto depois), mas dá a impressão de haver dois `R` diferentes.
**É o mesmo `R`** — um fechado, o outro aberto.

---

## 4. A construção de `R` — definição, identidades, resultado

### 4.1 O que é uma matriz de covariância

`R ≜ E[n n^H]` é `M × M`; a entrada `(a, b)` é `E[n_a · n_b*]`, ou seja **quanto o ruído na
antena `a` anda junto com o ruído na antena `b`**. Diagonal: potência em cada antena.
Fora da diagonal: correlação entre antenas.

`[ARTIGO :60]`
> "`n ~ CN(0, R)` denotes the additional white Gaussian noise (AWGN) with **`R ≜ E[n n^H]`**
> being the covariance matrix."

O símbolo `≜` significa "definido como" — não é resultado de conta nenhuma.

**Sobre `CN(0, R)`:** distribuição gaussiana complexa circularmente simétrica. O primeiro
argumento é o vetor de médias, o segundo a matriz de covariância — uma gaussiana fica
completamente determinada por esses dois parâmetros. "Circularmente simétrica" implica
`Var(Re) = Var(Im) = σ²/2` em cada antena, o que importa para o dimensionamento de ponto fixo.

**Simplificação implícita:** a definição geral de covariância é `E[(n − E[n])(n − E[n])^H]`.
Como `E[n] = 0`, colapsa para `E[n n^H]`. O artigo já escreve a versão simplificada.

### 4.2 As duas identidades de livro

Nenhuma das duas é específica deste artigo. São teoremas gerais.

**Identidade 1 — covariância sob transformação linear.**
Se `x = A z` com `A` determinística, então `Cov(x) = A · Cov(z) · A^H`.

```
E[x x^H] = E[(Az)(Az)^H] = E[A z z^H A^H] = A · E[z z^H] · A^H
```

Aplicada aqui: `Cov(H̄ s̄) = H̄ · (βI) · H̄^H = β H̄ H̄^H`.

*Sentido físico:* o canal pega `r` sinais independentes e os espalha por `M` antenas. Sinais
descorrelacionados na origem chegam correlacionados no destino, porque cada antena recebe uma
mistura dos mesmos `r`. **A correlação é criada pelo canal.**

**Identidade 2 — covariância de soma de independentes.**
Se `u` e `v` são independentes e de média zero, `Cov(u + v) = Cov(u) + Cov(v)`.

```
E[(u+v)(u+v)^H] = E[uu^H] + E[uv^H] + E[vu^H] + E[vv^H]
                             \___/     \___/
                        ambos zero: independentes e de média zero
```

### 4.3 Montando

```
n   =   H̄ s̄        +        n̄
        \____/               \_/
Cov:  β H̄ H̄^H       +      σ² I        <- Identidade 2
      \_______/
     Identidade 1
```

`[ARTIGO :113]`
> "Then, the colored noise covariance matrix **`R = β H̄ H̄^H + σ² I`**, where `β` is the power
> of interference signals. **In this scenario, `R` becomes non-block-diagonal.**"

### 4.4 O que é definição, o que é teorema, o que é hipótese

Esta tabela é a resposta a "isso é definição de livro?", e é o que sustenta a defesa:

| Camada | Item | Contestável? |
|---|---|---|
| **Definição** | `R ≜ E[n n^H]` | Não. É o significado de "covariância". |
| **Identidade** | `Cov(Az) = A Cov(z) A^H` | Não. Teorema geral. |
| **Identidade** | `Cov(u+v) = Cov(u) + Cov(v)` se independentes | Não. Teorema geral. |
| **Hipótese** | `E[s̄ s̄^H] = β I_r` (H3) | **Sim.** Potências iguais é simplificação. |
| **Hipótese** | `E[n̄ n̄^H] = σ² I` (H4) | Na prática, sim. |
| **Hipótese** | `s̄` independente de `n̄` (H5) | Não, é evidente. |
| **Hipótese** | `H̄` determinística (H6) | **Sim**, e o artigo admite. |
| **Resultado** | `R = β H̄H̄^H + σ² I` | Segue das linhas acima. |

**`R = βH̄H̄^H + σ²I` não é definição nem teorema — é o resultado de aplicar duas identidades
gerais a quatro hipóteses de modelagem.**

### 4.5 Por que `n n^H` sozinho não é covariância

Uma realização de `n n^H` tem **posto 1** — todas as colunas são múltiplas de `n`. É
massivamente singular e não descreve estrutura espacial nenhuma, apenas a direção de `n`
naquele instante.

A covariância emerge só ao **somar muitas**: cada `n^i (n^i)^H` contribui posto 1, e a soma de
`N` delas tem posto `min(N, M)`. Daí a exigência `N ≫ K` de `:123`, e daí `R̂_cc` (`Mc × Mc`,
com `N = 192`) sair de posto cheio com folga de 6x a 24x conforme a configuração.

---

## 5. As hipóteses do artigo (H1 a H9)

### H1 — O ruído na BS é colorido, não branco

**Enunciado:** `R` não é diagonal.

`[ARTIGO :105]`
> "the noise at the BS is often colored due to the existence of **interference signals from
> non-target UEs in neighboring cells** [21], [22]."

Apoia-se em literatura anterior, não em derivação própria.

**Por que é a hipótese central.** A nota de rodapé 3 (`[ARTIGO :819]`, presa a `:105`) mostra
exatamente o que se perde ao assumi-la:

> "the LMMSE receiver in Eq. (3) would degenerate into `(H^H H + (σ_0²/E_s) I)^{-1} H^H`, where
> `σ_0²` is the noise power of the AWGN. In this case, **`H^H H` can be computed as
> `Σ_{c=1}^C H_c^H H_c` by aggregating the low-dimensional local information from each DU.**
> Subsequently, the low-dimensional inversion result can be broadcast to each DU for local
> equalizer computation."

Traduzindo: **com ruído branco o problema é trivial.** Cada DU calcula uma `K × K`, soma-se
tudo, inverte-se uma única `K × K`, e acabou. Sem BCD, sem anel, sem iteração, e sem nenhuma
inversão `Mc × Mc`.

**Consequência:** o módulo deste TG existe por causa de H1. Se o ruído fosse branco, não
haveria inversor `Mc × Mc` para projetar.

### H2 — A cor vem de interferência de UEs vizinhos

**Enunciado:** `n = H̄ s̄ + n̄`, com `r` UEs não-alvo.

**Justificativa e alcance** — nota de rodapé 1 (`[ARTIGO :815]`):
> "Practically, **channel estimation errors can also be modeled as a specific form of colored
> background noise** [23], [24]. Note that **our proposed decentralized methods apply to all
> colored noise scenarios.**"

Importante para a defesa: a interferência é **um exemplo**, não o único caso. O método — e
portanto o hardware — vale para qualquer `R` cheia. Se questionarem "e se a interferência não
for dominante?", a resposta está aqui.

**Consequência para o hardware: nenhuma.** O datapath recebe `R̂_cc` estimada de amostras reais
e não sabe de onde veio a cor.

### H3 — Os `r` interferentes são independentes e têm potência `β` cada

**Esta é a hipótese que o artigo NÃO enuncia explicitamente.** Ela está implícita na fórmula.

`[ARTIGO :113]` diz apenas que "`β` is the power of interference signals". Para
`R = β H̄H̄^H + σ²I` ser verdadeira, é preciso que `E[s̄ s̄^H] = β I_r`, o que embute:

| Parte da matriz | O que assume |
|---|---|
| diagonal `= β` | todos os `r` interferentes transmitem com **a mesma potência** |
| fora da diagonal `= 0` | interferentes distintos **não se coordenam** |

A segunda é natural — são UEs de células diferentes. A primeira é **simplificação**: no mundo
real daria `diag(β_1, ..., β_r)`.

`[NOSSO]` Marcar isto como hipótese implícita é relevante para a metodologia do TG: é um ponto
onde o artigo omite e nós explicitamos.

### H4 — O ruído térmico é branco e uniforme

**Enunciado:** `n̄ ~ CN(0, σ² I)` (`[ARTIGO :113]`).

**Justificativa:** nenhuma explícita — é o modelo padrão de ruído térmico. A diagonal segue de
cada cadeia de RF gerar o seu ruído independentemente.

**Papel estrutural `[NOSSO]`:** é o `σ² I` que torna `R` inversível. Sozinho, `β H̄ H̄^H` tem
posto `r = 8` numa matriz `128 × 128` — singular. **O ruído térmico é o que garante o Cholesky.**

### H5 — `s̄` e `n̄` são independentes, ambos de média zero

**Justificativa:** não enunciada; evidente por construção. `s̄` é gerado num transmissor a
centenas de metros; `n̄` é agitação térmica dentro do próprio receptor.

**Onde foi usada:** mata os termos cruzados na Identidade 2. Sem ela, `R` teria termos
`H̄ E[s̄ n̄^H]` e a fórmula não fecharia.

### H6 — O canal `H` é perfeitamente conhecido e determinístico

`[ARTIGO :63]`
> "**Assuming the channel matrix `H` is perfectly known**, LMMSE equalization aims to find a
> linear estimate by solving the following problem:"

**Justificativa** — nota de rodapé 2 (`[ARTIGO :817]`):
> "Decentralized channel estimation is also a crucial problem for DBP implementation. Several
> papers have focused on this topic, such as [26]. However, in our paper, **we suppose that the
> decentralized channel estimation has been already accomplished** and focus on decentralized
> detection/equalization design."

Recorte de escopo declarado, não afirmação sobre o mundo. E dialoga com H2: erro de estimação
de canal vira ruído colorido, ou seja, recai em H1.

**Onde foi usada:** permitiu `H̄` sair da esperança na Identidade 1. Determinística **dentro do
bloco de coerência** — o que varia entre realizações são os símbolos, não o canal. É a mesma
premissa que sustenta o reuso de `W` (`[ARTIGO :61]`, `:561`).

### H7 — `R` pode ser estimada por médias, inclusive em frequência

Nota de rodapé 4 (`[ARTIGO :821]`, presa a `:117`):
> "The noise covariance has been shown to **stay constant over a wide frequency interval** [29],
> and thus **can be estimated via averaging over frequency** in practical wideband systems."

`[NOSSO]` Duas consequências, ambas relevantes para o mapa de tempo:

1. As `N = 192` amostras **não precisam ser 192 símbolos no tempo** — podem ser colhidas ao
   longo da frequência, dentro de um mesmo símbolo OFDM. Isso torna `N = 192` muito mais barato
   do que aparenta.
2. **A covariância tem escala de coerência própria, mais larga que a do canal.** `H` muda a cada
   PRB (`[ARTIGO :614]`); `R` permanece constante "over a wide frequency interval". São escalas
   diferentes — logo `R̂_cc` tem cadência de atualização **mais folgada** que `H_c`.

O item 2 interage diretamente com o ponto em aberto PRB vs. banda de coerência já registrado no
`fases_formulacao_vs_filtragem.md`.

### H8 — `N ≫ K`

`[ARTIGO :123]`
> "which is done by averaging the noise samples in **`N` pilot resource elements (REs)**. Here,
> **`N ≫ K` holds to ensure the accuracy of estimation**, and `n^i ∈ ℂ^{M×1}` is the noise sample
> in the `i`-th pilot RE."

**Justificativa:** estatística amostral, e geometricamente o argumento de posto da Seção 4.5.

`[NOSSO]` **Para o nosso módulo:**

| Config | `Mc` | `N` | Folga `N/Mc` |
|---|---|---|---|
| A, D, E | 16 | 192 | 12x |
| B, F | 8 | 192 | 24x |
| C | 32 | 192 | 6x |

Em todas, `N ≫ Mc`. `R̂_cc` sai definida positiva quase certamente, logo **o inversor nunca
recebe matriz algebricamente singular: dispensa lógica de pivotamento, detecção de posto
deficiente e ramo para matriz indefinida.** Simplificação de hardware justificável por citação.

> **Cuidado — o que este argumento NÃO garante.** Ele é **algébrico**, não numérico. Uma matriz
> matematicamente definida positiva mas mal condicionada pode, em **ponto fixo**, produzir um
> pivô não-positivo por arredondamento, fazendo a raiz quadrada do Cholesky falhar numa matriz
> comprovadamente inversível. E a Seção 6.1 mostra que estamos exatamente nesse regime: IoT de
> 20 dB empurra o número de condição para cima.
>
> Portanto: **se um caminho de fallback para pivô não-positivo pode ser omitido é questão em
> aberto**, a ser decidida pelo sweep de ponto fixo da Seção 6.1 — não pela álgebra desta seção.

### H9 — Os `K` UEs-alvo são independentes e têm energia `E_s` cada

`[NOSSO]` **Hipótese implícita, como a H3 — o artigo nunca a escreve.**

**Enunciado:** `E[s s^H] = E_s I_K`.

O artigo define apenas `E_s` (`[ARTIGO :79]`: "where `E_s` denotes the average energy per
symbol") e usa a forma **resultante** na eq. (3) (`[ARTIGO :75]`):

```
W_MMSE = ( H^H R^-1 H + (1/E_s) I )^-1 H^H R^-1
```

Essa forma só é o filtro LMMSE ótimo se `E[s s^H] = E_s I_K`. O que isso embute:

| Parte da matriz | O que assume |
|---|---|
| diagonal `= E_s` | todos os `K` UEs-alvo transmitem com **a mesma energia média** |
| fora da diagonal `= 0` | os UEs-alvo **não se coordenam** entre si |

**É a mesma estrutura da H3, um andar acima:**

| Hipótese | Sobre quem | Onde está |
|---|---|---|
| `E[s̄ s̄^H] = β I_r` (H3) | os `r` UEs não-alvo | implícita em `R = βH̄H̄^H + σ²I` (`:113`) |
| `E[s s^H] = E_s I_K` (H9) | os `K` UEs-alvo | implícita na eq. (3) (`:75`) e na eq. (30) (`:504`) |

**Onde é usada:** é ela que produz o termo `E_s H_c H_c^H` do fator invertido da eq. (30).
Ver Seção 10.2.

**Ressalva de enquadramento** — `[ARTIGO :383]`, sobre o problema (24):

> "The objective function of the above problem has **only one random variable `s`**, and the
> other variables are **deterministic**."

No problema de otimização do artigo, as amostras `n^i` são tratadas como vetores
**determinísticos armazenados**, não como variável aleatória: a esperança é só sobre `s`, e o
ruído entra por média empírica `(1/N) Σ_i`. Os dois enquadramentos dão a **mesma matriz**,
porque `(1/N) Σ_i n_c^i (n_c^i)^H` é justamente o estimador de `R_cc` — e a nota 5 (`:821`)
autoriza tratar os dois como um só objeto.

---

## 6. De onde vem `β`

**O que é:** a potência de transmissão de cada UE não-alvo. `[ARTIGO :113]` — "`β` is the power
of interference signals"; `[ARTIGO :577]` — "`β` signifies the power of non-target UEs".

**Como se separa de `H̄`:** `β` é a **fonte**, `H̄` é o **caminho**. `H̄` é gerada no QuaDRiGa e
traz perda de percurso e desvanecimento (`[ARTIGO :577]`: "considers both large and small-scale
fading"). A potência de interferência que chega à antena `a`, vinda do interferente `k`, é
`β · |h̄_{ak}|²`.

**Como o artigo o controla** (`[ARTIGO :577]`):
> "The **interference over thermal (IoT)** is used to measure the intensity of interference
> relative to background noise, i.e., **`IoT = 10 log₁₀((β + N_0)/σ²)`**. Large IoT leads to
> significant interference, i.e., the off-diagonal elements of the noise covariance matrix
> [tornam-se maiores]"

`β` não é um número fixo: é o **botão** com que o artigo varia a severidade do cenário.
`[ARTIGO :593]` registra que a Fig. 8(f) usa **`IoT = 20 dB`**, o caso duro.

### 6.1 O ponto que mais importa: `β` nunca entra no datapath

`[NOSSO]` O hardware não mede `β`, não estima `β`, não recebe `β`. Ele vê apenas `R̂_cc`, que já
traz o efeito de `β` embutido nas amostras. **`β` é parâmetro de geração de cenário de teste,
não de operação.**

Onde `β` afeta o projeto, indiretamente: **IoT alto implica `R` mal condicionada, o que implica
mais bits no ponto fixo.** O número de condição de `R_cc` escala grosseiramente com
`(β·λ_max + σ²)/σ²`. Consequência metodológica: **o sweep de precisão contra SER tem que ser
feito no IoT mais alto (20 dB), não no caso médio.**

### 6.2 Parâmetros de simulação relacionados

`[ARTIGO :577]`
> "The number of target and non-target UEs is both set to `K = 8`, and there are `N = 192` noise
> samples. The channel matrix is generated from the QuaDRiGa platform... UEs are uniformly
> distributed within a 120° sector of radius 50 ~ 100 m centered at BS. The signal-to-noise
> ratio (SNR) is defined as `SNR = 10 log₁₀(E_s/σ²)`."

É daqui que vem o `r = 8` da grade de parâmetros do `constraints.csv`: `r` é herdado de
`r = K = 8`, e é usado principalmente pela variante LRD (fora de escopo).

---

## 7. A armadilha da nota de rodapé 5 — o artigo funde `R̂` e `R`

Nota de rodapé 5 (`[ARTIGO :821]`, presa ao final de `:123`):

> "Although `R̂` is an approximate estimate of `R`, in practice, the estimation error is small
> when `N` is large. More importantly, we can only obtain the estimation `R̂` rather than
> statistical covariance `R`. Therefore, **for simplicity of notation, we make no distinction
> between `R̂` and `R` in the rest of this paper.**"

**A partir de `:123` o artigo abandona o chapéu.** Quando escreve `R_cc` depois disso — inclusive
na eq. (7) — está querendo dizer `R̂_cc`, a estimativa amostral.

`[NOSSO]` **Implicações:**

1. É a principal causa de confusão ao ler o artigo linearmente: parece haver dois objetos onde
   há um, e parece haver um onde há dois.
2. **No TG vale manter a distinção**, justamente porque ela some no texto original. O que o
   hardware processa é sempre a estimativa.
3. A eq. (30) (`[ARTIGO :504]`) escreve o termo por extenso como
   `(1/N) Σ_i n_c^i (n_c^i)^H` — ou seja, ali o artigo *volta* a ser explícito. Esse termo é
   exatamente `R̂_cc`.

---

## 8. Os inputs do Algoritmo 3

`[ARTIGO :408]`
> "**Input:** `y_c, H_c, {n_c^i}_{i=1}^N, c = 1,2,...,C`, `E_s`, and total iteration number `T`."

Dimensões para a config A (`M = 128`, `C = 8`, `Mc = 16`, `K = 8`, `N = 192`):

| Símbolo | O que é | Dimensão | Onde vive | Muda a cada | Linha |
|---|---|---|---|---|---|
| `y_c` | sinal recebido no cluster `c` | `ℂ^{16×1}` | local ao DU `c` | RE (3300/símbolo) | 96, 104 |
| `H_c` | matriz de canal local | `ℂ^{16×8}` | local ao DU `c` | PRB (275/símbolo) | 104 |
| `{n_c^i}` | `N` amostras de ruído locais | 192 vetores `ℂ^{16×1}` | local ao DU `c` | bloco de coerência | 125 |
| `C` | número de clusters/DUs | escalar, 8 | parâmetro de arquitetura | nunca | 85 |
| `E_s` | energia média por símbolo | escalar real | parâmetro do sistema | nunca | 79 |
| `T` | número de iterações BCD | escalar inteiro | parâmetro de projeto | nunca | 461 |

### 8.1 Observações por item

**`y_c`** — `[ARTIGO :96]` particiona `y = [y_1^T, ..., y_C^T]^T` conforme os clusters de
antenas. **É o único input que a fase de formulação não usa:** aparece só no bloco
`Equalizer filter`. Para o nosso módulo, `y_c` é irrelevante.

**`H_c`** — `[ARTIGO :104]`
> "`H_c ∈ ℂ^{Mc×K}` and `n_c ∈ ℂ^{Mc×1}` denote the local channel matrix and the local noise
> vector with respect to cluster `c`... Note that, **`H_c` and `y_c` are only known locally to
> the DU `c` and are not allowed to be directly exchanged among DUs** to save bandwidth overhead."

Essa última frase é a razão de existir do artigo: se pudessem trocar `H_c`, bastaria juntar
tudo e inverter centralizadamente.

**`{n_c^i}`** — as amostras vêm de **REs de piloto** (`[ARTIGO :123]`), não de REs de dados.
Chegam na fase de pilotos e valem para todo o bloco de coerência; não têm a cadência de
2,525 ns dos dados. Ver também H7: podem ser colhidas em frequência.

**`T`** — `[ARTIGO :461]`
> "In the simulation part, **only the first four iterations** of the BCD algorithms are
> considered due to bandwidth and computation limitations in practice. Thus the number `T` of
> iterations can be chosen according to both the above two factors."

A Tabela I usa `T = 2`. E `[ARTIGO :585]`: "only 2 to 3 iterations are sufficient to approach
the performance of the centralized LMMSE method for all cases."

### 8.2 O que o módulo de inversão realmente consome

Dos seis inputs, o inversor precisa de dois:

```
G_c = E_s · H_c H_c^H  +  (1/N) Σ_i n_c^i (n_c^i)^H
      \______________/     \____________________/
        precisa de H_c       precisa de {n_c^i}  ( = R̂_cc )
```

`y_c`, `C` e `T` não entram. `E_s` entra como escalar de escala.

### 8.3 Nota de memória local

`[NOSSO]` O inversor em si só precisa do acumulado `R̂_cc` (`16 × 16`), **não** das 192 amostras
individuais. Mas o lado esquerdo da eq. (30) contém
`Σ_i (b_{c-1,i}^l − W_c^{l-1} n_c^i)(n_c^i)^H`, que casa cada `b_{c-1,i}` com o seu `n_c^i`
correspondente. Logo o DU **precisa armazenar os 192 vetores individualmente**: em config A,
`192 × 16 = 3072` números complexos por DU.

É memória, não aritmética — mas é o item dominante do orçamento de armazenamento local, e
explica por que `N` aparece na conta de banda de `[ARTIGO :571]` como `2NK`: são `N` vetores
`b_{c,i}` de dimensão `K` circulando no anel, além da matriz `A_c`.

---

## 9. O bloco `Preprocessing` — a eq. (7) e a semeadura de `A` e `b`

O bloco (`[ARTIGO :414-421]`) faz **duas coisas independentes**, fáceis de confundir.

### 9.1 Linha 2 — o chute inicial `W^0` pela eq. (7)

> `Initialize W^0 using (7) in a decentralized manner;`

A eq. (7) é o equalizador **BDAC-MMSE** — *Block Diagonal Approximation of Covariance*, nome
dado em `[ARTIGO :556]` e `:583`.

A ideia (`[ARTIGO :131]`):
> "approximating `R` with a block diagonal matrix, denoted by
> `R_B ≜ blkdiag(R_11, R_22, ..., R_CC)`, where all off-diagonal blocks are set to zero."

Com essa aproximação a inversa se fatora (`[ARTIGO :135-136]`, eq. 7):

```
(H^H R_B^-1 H + (1/E_s) I)^-1 H^H R_B^-1
  = ( Σ_{c=1}^C H_c^H R_cc^-1 H_c + (1/E_s) I )^-1  x  [ H_1^H R_11^-1 , ... , H_C^H R_CC^-1 ]
     \_________________________________________/         \______________________________/
                    K x K  (global)                        o bloco c é local ao DU c
```

`[ARTIGO :140]`
> "each DU `c = 1,2,...,C` first computes `H_c^H R_cc^{-1} H_c` **locally**, which is then
> collected together for summation and inversion operations. Finally, the matrix inverse result
> is **broadcasted to all DUs**, allowing them to compute their local equalization matrices."

**Aqui já existem duas inversões, e nenhuma é a da eq. (30):**

| Inversão | Dimensão | Onde | Frequência |
|---|---|---|---|
| `R_cc^{-1}` | `Mc × Mc` (16×16) | local, em cada DU | 1 por DU por bloco de coerência |
| `(Σ_c H_c^H R_cc^{-1} H_c + (1/E_s)I)^{-1}` | `K × K` (8×8) | global | 1 por PRB |

São os dois primeiros dos três sítios de inversão registrados no `constraints.csv`. Note que a
segunda é **pequena** — dimensão de UEs, não de antenas.

Complexidade da inicialização, `[ARTIGO :556]`: `O(M·Mc² + N·M·Mc)`.

`[NOSSO]` **Ressalva de arquitetura:** "collected... and broadcasted" descreve naturalmente a
estrela, que tem CU. No daisy chain não existe CU (`[ARTIGO :87]`), então esse padrão tem que
ser realizado como duas voltas no anel. O artigo não detalha isso.

**Por que basta um chute grosseiro:** `[ARTIGO :585]` — "only 2 to 3 iterations are sufficient
to approach the performance of the centralized LMMSE method". O BCD corrige a aproximação
bloco-diagonal em pouquíssimas voltas. E `[ARTIGO :826]` (nota 8) esclarece que o pequeno gap
residual nas figuras é por número insuficiente de iterações: "after sufficient iterations, they
will overlap completely."

### 9.2 Linhas 3 a 8 — semeando `A` e `b`

```
A_0^0     <- 0                                   (K x K)
b_{0,i}^0 <- 0,  i = 1..N                        (N vetores K x 1)

for c = 1 to C:
    A_0^0     <- A_0^0     + W_c^0 H_c
    b_{0,i}^0 <- b_{0,i}^0 + W_c^0 n_c^i
```

Ao fim do laço:

```
A_0^0     = Σ_{c=1}^C W_c^0 H_c    =  W^0 H       (o produto GLOBAL)
b_{0,i}^0 = Σ_{c=1}^C W_c^0 n_c^i  =  W^0 n^i     (o produto GLOBAL)
```

**`A` e `b` são os produtos globais `W·H` e `W·n^i` mantidos como um total corrente.** Nenhum DU
os calcula sozinho — daí a soma percorrer todos os `C`.

`[ARTIGO :438]` define os dois como *interaction variables*: `A_c^l ∈ ℂ^{K×K}` e
`{b_{c,i}^l ∈ ℂ^{K×1}}_{i=1}^N`.

### 9.3 Por que essas duas quantidades, e não outras

`[ARTIGO :398]`
> "We observe that **`Σ_{j≠c} W_j H_j` and `{Σ_{j≠c} W_j n_j^i}` is needed for computing `W_c*`**,
> and all the other terms in (26) can be computed via local information at DU `c`."

A eq. (26) (`[ARTIGO :454]`) é a solução ideal do subproblema e traz esses somatórios
explicitamente. O DU `c` precisa da contribuição de **todos os outros**, mas não pode receber os
`H_j` e `n_j^i` deles. O truque:

```
Σ_{j≠c} W_j H_j  =  (soma de TODOS)  -  (a minha própria parcela)
                 =      A_{c-1}      -    W_c^{l-1} H_c
```

E é exatamente isso que aparece na eq. (30) (`[ARTIGO :504]`): o fator
`(I_K − A_{c-1}^l + W_c^{l-1} H_c)` **é** `(I_K − Σ_{j≠c} W_j H_j)`, e
`(b_{c-1,i}^l − W_c^{l-1} n_c^i)` **é** `Σ_{j≠c} W_j n_j^i`. As eqs. (28)/(29)
(`[ARTIGO :442-443]`) fazem o inverso — recolocam a parcela nova no total antes de passar adiante.

**Cada DU carrega o total e subtrai a sua própria contribuição desatualizada para recuperar
"todos os outros".** É isso que permite trafegar `K × K` em vez de `Mc × K` — `[ARTIGO :447]`:
"the local equalization matrices act as local compression matrices".

Por isso a inicialização precisa ser o **total**, e não zero: se `A_0^0` fosse zero, a primeira
subtração devolveria a soma errada.

### 9.4 O laço `for c = 1 to C` é uma volta no anel

`[NOSSO]` No daisy chain esse `for` não é laço de software num lugar só: é uma volta física.
O DU 1 soma a sua parcela e passa; o DU 2 soma e passa; o DU `C` fecha o anel devolvendo
`A_0^0` e `{b_{0,i}^0}` completos ao DU 1, onde a primeira iteração BCD começa.
Desenhado em `diagramas/anel_formulacao.puml`.

### 9.5 Custos do bloco

| Linha | O que faz | Custo dominante |
|---|---|---|
| 2 | `W^0` pela eq. (7) | 2 inversões (`Mc×Mc` local + `K×K` global), `O(M·Mc² + N·M·Mc)` |
| 3-4 | zera `A` e `b` | nada |
| 5-8 | acumula os totais globais numa volta do anel | `C` produtos `K×Mc · Mc×K` + `C·N` produtos `K×Mc · Mc×1` |

`[NOSSO]` O termo `C·N` da linha 7 é o pesado: com `N = 192` e `C = 8`, são 1536 produtos
matriz-vetor só para semear os `b`.

**Este bloco inteiro roda uma vez por bloco de coerência**, não a cada símbolo — é o que o
`/N_coh` do primeiro termo de `[ARTIGO :571]` indica. É a parte mais barata do orçamento de
tempo, e a melhor candidata a caminho lento em software.

---

## 10. O fluxo completo — da hipótese ao silício

O diagrama tem **dois ramos** — sinal e ruído — porque `y_c = H_c s + n_c` tem duas parcelas,
e a matriz que o nosso módulo fatora é a covariância dessa soma.

> Versão em PlantUML, com as mesmas citações e hipóteses: **`diagramas/modelo_ruido.puml`**.

```
              RAMO DO SINAL                          RAMO DO RUÍDO
              (K UEs alvo)                    (r interferentes + térmico)

   s   símbolos dos K UEs alvo        s̄  interferentes        n̄  térmico
   E[s s^H] = E_s I_K       [H9]      E[s̄ s̄^H] = β I_r [H3]   E[n̄ n̄^H] = σ² I  [H4]
   "K UEs independentes,              "r UEs independentes,    "branco e
    energia E_s cada"                  potência β cada"         uniforme"
   IMPLÍCITA na eq. (3), :75          IMPLÍCITA em :113
        │                                   │                        │
        │ canal H   [H6]                    │ canal H̄  [H6]          │
        │ Identidade 1                      │ Identidade 1           │
        ▼                                   ▼                        ▼
      H s                                  H̄ s̄ ─────────── + ───────┘
      Cov = E_s H H^H                                 │  Identidade 2  [H5]
        │                                             ▼
        │                          n = H̄ s̄ + n̄                    (eq. 5, :109)
        │                          R ≜ E[n n^H]                    (DEFINIÇÃO, :60)
        │                          R = β H̄ H̄^H + σ² I             (RESULTADO, :113)
        │                              \_______/  \____/
        │                               cheia,    diagonal, é quem
        │                               posto r   torna R inversível
        │                                             │
        │                          R é CHEIA -> R^-1 não fatora por cluster   [H1]
        │                          (nota 3, :819: se fosse branca, bastaria
        │                           UMA inversão K x K e não haveria este TG)
        │                                             │
        └──────────────── y = H s + n ────────────────┘             (eq. 1, :56)
                              │
                              │  particiona por clusters de antenas   (:96, :104)
                              ▼
                       y_c = H_c s + n_c        o que o DU c enxerga

   ========================== FRONTEIRA ==========================
      acima: teoria e motivação.    abaixo: o que vira silício.
   ===============================================================
                              │
          ┌───────────────────┴────────────────────┐
          │                                        │
          │ H_c dado pela estimação                │ R é E[·] -> inatingível.
          │ de canal, suposta pronta  [H6]         │ Estima com N=192 amostras [H8]
          │                                        │ colhidas em FREQUÊNCIA    [H7]
          │                                        ▼
          │                          R̂ = (1/N) Σ_i n^i (n^i)^H      (eq. 6, :119)
          │                                        │
          │                          cada DU só alcança o bloco DIAGONAL
          │                          (os cruzados exigiriam M x N: proibido, :130)
          │                                        ▼
          ▼                                     R̂_cc                        (:125)
   E_s H_c H_c^H                          16x16, posto 16
   16x16, posto <= K = 8                  DEFINIDA POSITIVA
   SINGULAR sozinha
          │                                        │
          └──────────────────── + ─────────────────┘
                                ▼
        G_c = E_s H_c H_c^H + R̂_cc  =  R̂_{y_c y_c}
        A COVARIÂNCIA (ESTIMADA) DO SINAL RECEBIDO LOCAL
        Mc x Mc, hermitiana definida positiva
                                │
                                ▼
        É ISTO QUE O NOSSO MÓDULO FATORA     (fator direito da eq. 30, :504)
```

**O que atravessa a fronteira:** dos objetos do modelo estatístico, apenas **dois** — `H_c` e
`R̂_cc` — mais o escalar `E_s`. Nem `β`, nem `H̄`, nem `σ²`, nem `s̄`, nem o próprio `s` chegam
ao hardware. Eles explicam *por que* `G_c` é cheia e mal condicionada, mas o datapath recebe
uma matriz hermitiana definida positiva e a fatora, sem saber de onde ela veio.

**As hipóteses justificam o projeto; não parametrizam a implementação.**

### 10.1 Estrutura de `G_c`

`[NOSSO]` A mesma estrutura "singular + definida positiva" da Seção 4 reaparece um nível abaixo:

```
G_c  =  E_s H_c H_c^H     +     R̂_cc
        \______________/        \____/
        16x16, mas nasce        16x16,
        de uma 16x8:            posto 16
        posto <= K = 8          DEFINIDA POSITIVA
        SINGULAR sozinha
```

Quem garante a inversibilidade de `G_c` é `R̂_cc`, definida positiva porque `N ≫ Mc` (H8).
Consequência: **hermitiana definida positiva garantida, logo Cholesky em vez de LU com
pivotamento, e metade da matriz é redundante** (`G_ab = G_ba*`) — economia direta de área.

Vale a mesma ressalva da Seção 5 (H8): a garantia é **algébrica**. Se o Cholesky em ponto fixo
dispensa tratamento de pivô não-positivo é questão numérica, decidida pelo sweep da Seção 6.1.

### 10.2 `G_c` é a covariância do sinal recebido local

`[NOSSO]` — o artigo não nomeia esta matriz nem lhe dá interpretação. A leitura abaixo é nossa,
mas é verificável em duas linhas.

O DU `c` recebe `y_c = H_c s + n_c` (`[ARTIGO :96]`, `:104`). A covariância disso é:

```
E[y_c y_c^H] = E[(H_c s + n_c)(H_c s + n_c)^H]
             = H_c E[s s^H] H_c^H  +  E[n_c n_c^H]        <- Identidade 2, cruzados morrem
             = H_c (E_s I_K) H_c^H  +  R_cc               <- Identidade 1 e H9
             = E_s H_c H_c^H + R_cc
```

São **as mesmas duas identidades da Seção 4.2**, aplicadas um nível acima. Logo:

> **`G_c` é `R_{y_c y_c}`** — a covariância do sinal recebido no cluster `c` — com `R̂_cc` no
> lugar de `R_cc`, porque o hardware só dispõe da estimativa.

**Isso explica de onde vem cada propriedade que já tínhamos deduzido separadamente:**

| Propriedade de `G_c` | Por quê |
|---|---|
| hermitiana | toda matriz de covariância é |
| semidefinida positiva | `x^H R_{yy} x = E[abs(y_c^H x)²] ≥ 0` |
| definida positiva | `R̂_cc` é PD porque `N ≫ Mc` (H8) |
| autovalores = potências | são potências de sinal recebido por direção espacial |

A última linha dá uma leitura de escala útil para ponto fixo: o maior autovalor é da ordem da
potência recebida total (sinal + interferência dominante); o menor, da ordem de `σ²`. **A razão
entre eles é o número de condição — e é por isso que o IoT o governa** (Seção 6.1, NOTA 23).
Isso permite estimar a faixa dinâmica necessária analiticamente, antes de simular.

### 10.3 A eq. (30) é a equação normal de Wiener resolvida por bloco

`[NOSSO]` — o artigo chega à eq. (26) derivando o MSE, não por este caminho. Mas a estrutura é
esta, e ela esclarece o porquê da forma da equação.

Reescrevendo a eq. (26) (`[ARTIGO :454]`) em linguagem de covariâncias:

```
W_c  =  ( R_{s y_c}  −  Σ_{j≠c} W_j R_{y_j y_c} )  ·  R_{y_c y_c}^{-1}
          \_______/       \________________/          \___________/
        o que eu quero   o que os outros DUs          o que eu tenho
        vs. o que tenho   já explicaram
```

Conferindo termo a termo contra a eq. (26):

| Termo da eq. (26) | É |
|---|---|
| `E_s I_K H_c^H` | `E[s y_c^H] = R_{s y_c}` |
| `E_s H_j H_c^H + (1/N)Σ_i n_j^i (n_c^i)^H` | `E[y_j y_c^H] = R_{y_j y_c}` |
| o fator invertido | `E[y_c y_c^H] = R_{y_c y_c}` |

**É literalmente a equação normal de Wiener (`W = R_{sy} R_{yy}^{-1}`), particionada por
blocos e resolvida por Gauss-Seidel** — um bloco por vez, descontando o que os outros já
contribuíram.

Duas consequências:

1. **Explica por que o fator invertido não tem índice `l`.** `R_{y_c y_c}` depende só de dados
   locais (`H_c`, `{n_c^i}`) e nunca de `W`. É o lado esquerdo que carrega a iteração. Este é o
   mesmo achado registrado na NOTA 2 do `constraints.csv` e em
   `diagramas/algoritmo3_hardware.puml`, agora com justificativa estrutural além da sintática.
2. **Os blocos cruzados `R̂_jc` aparecem na equação, mas nunca são materializados.** Chegam
   comprimidos dentro de `A_c` e `b_{c,i}` (Seção 9.3). É a economia de banda do artigo vista
   pelo ângulo estatístico: o anel transporta `Σ_{j≠c} W_j R_{y_j y_c}` já reduzido à dimensão
   `K`, em vez das matrizes `R_jc` de dimensão `Mc × Mc`.

---

## 11. Índice de citações

| Afirmação | Linha |
|---|---|
| Modelo de banda base `y = Hs + n` (eq. 1) | 56 |
| `R ≜ E[n n^H]`; `n ~ CN(0, R)` | 60 |
| CSI quase constante entre símbolos; reuso de `W` | 61 |
| "Assuming the channel matrix `H` is perfectly known" | 63 |
| Problema LMMSE `min_W E[‖Wy − s‖²]` (eq. 2) | 67 |
| `W_MMSE = (H^H R^-1 H + (1/E_s)I)^-1 H^H R^-1` (eq. 3) | 75 |
| `E_s` = energia média por símbolo; `ŝ = W y` | 79 |
| DBP divide `M` antenas em `C` clusters de `Mc` | 85 |
| Topologia daisy chain: sem CU, anel, um só DU no decodificador | 87 |
| Partição de `y`, `H`, `n` por cluster | 96 |
| `H_c`, `n_c` locais; proibido trocar entre DUs | 104 |
| Ruído colorido por interferência de UEs vizinhos | 105 |
| Eq. (5): `y = Hs + H̄s̄ + n̄` | 109 |
| `H̄`, `s̄`, `n̄`, `β`, `σ²`; `R = βH̄H̄^H + σ²I`; não bloco-diagonal | 113 |
| Eq. (6): `R̂ = (1/N) Σ_i n^i (n^i)^H` | 119 |
| `N` REs de piloto; `N ≫ K` | 123 |
| Partição de `n^i` por cluster; `R_mn = E[n_m n_n^H]` | 125 |
| Trocar amostras custaria `M × N`: proibitivo | 130 |
| `R_B ≜ blkdiag(R_11,...,R_CC)` | 131 |
| Eq. (7) — BDAC-MMSE | 135-136 |
| Implementação descentralizada da eq. (7) | 140 |
| `W = [W_1,...,W_C]`, `W_c ∈ ℂ^{K×Mc}` | 383 |
| Gauss-Seidel, minimização sequencial | 392 |
| `Σ_{j≠c} W_j H_j` e `{Σ_{j≠c} W_j n_j^i}` são necessários | 398 |
| Algoritmo 3 completo | 407-436 |
| Linha de `Input` do Algoritmo 3 | 408 |
| Bloco `Preprocessing` | 414-421 |
| Bloco `BCD iterations` | 422-429 |
| Bloco `Equalizer filter` | 430-434 |
| `A_c^l ∈ ℂ^{K×K}`, `b_{c,i}^l ∈ ℂ^{K×1}` — interaction variables | 438 |
| Eqs. (28) e (29) | 442-443 |
| Matrizes locais atuam como matrizes de compressão; hand-off no anel | 447 |
| Nota 6 — fechamento do anel: `A_0^l = A_C^{l-1}` | 450 |
| Problema (24); apenas `s` é aleatório, o resto é determinístico | 383 |
| Eq. (26) — forma ideal com `Σ_{j≠c}` explícito | 454 |
| Escolha de `T`; simulações usam 4 iterações | 461 |
| Eq. (30) — fator invertido **sem** índice `l` | 504 |
| Nome BDAC-MMSE; complexidade `O(M·Mc² + N·M·Mc)` | 556 |
| `N_coh` — reuso de `W` entre símbolos | 561 |
| Conta de banda em três termos | 571 |
| Setup de simulação; `β`; definição de IoT; QuaDRiGa | 577 |
| BDAC-MMSE é o ponto inicial dos algoritmos BCD | 583 |
| 2 a 3 iterações bastam | 585 |
| Fig. 8(f) usa `IoT = 20 dB` | 593 |
| Cada PRB tem uma matriz de canal diferente | 614 |
| Valores numéricos: `N=192`, `r=8`, `w=12`, `N_u=3300`, `N_PRB=275`, `N_sc,PRB=12`, `T_OFDM` | 640 |
| **Nota 1** — erro de estimação de canal também é ruído colorido | 815 |
| **Nota 2** — estimação de canal suposta já concluída | 817 |
| **Nota 3** — com ruído branco bastaria uma inversão `K×K` | 819 |
| **Nota 4** — `R̂` estimável por média em frequência | 821 |
| **Nota 5** — o artigo funde `R̂` e `R` a partir daqui | 821 |
| **Nota 7** — aproximação rank-`r` mesmo se `R` não for low-rank | 824 |
| **Nota 8** — o gap residual é por iterações insuficientes | 826 |

---

## 12. Descobertas desta sessão que afetam o `constraints.csv`

Três achados desta trilha mudam o mapa de restrições. Registrados como notas no CSV:

1. **`R̂_cc` tem cadência mais folgada que `H_c`** (H7, nota 4 do artigo, `:821`) — **NOTA 21**.
   A covariância
   é constante "over a wide frequency interval" e pode ser estimada por média em frequência.
   Interage com o ponto em aberto PRB vs. banda de coerência.
2. **O inversor nunca recebe matriz algebricamente singular** (H8 + Seção 10.1) — **NOTA 22**.
   `N = 192 ≫ Mc` garante `R̂_cc` definida positiva; somada a `E_s H_c H_c^H` (semidefinida),
   `G_c` é definida positiva. Dispensa pivotamento, detecção de posto e ramo para matriz
   indefinida. **Não** dispensa, por si só, tratamento de pivô não-positivo em ponto fixo —
   isso depende do item 3.
3. **O IoT governa o condicionamento, não a SNR** (Seção 6.1) — **NOTA 23**. O sweep de ponto
   fixo contra SER tem que ser feito no IoT alto (20 dB, `:593`), não no caso médio. É este
   sweep que decide a ressalva do item 2.
4. **`G_c` é a covariância do sinal recebido local `R_{y_c y_c}`** (Seções 10.2 e 10.3) —
   **NOTA 25**. Consequências: as propriedades hermitiana/definida positiva deixam de ser
   coincidência e passam a ser estruturais; os autovalores são potências recebidas, o que
   permite estimar a faixa dinâmica do ponto fixo analiticamente; e a eq. (30) revela-se a
   equação normal de Wiener por bloco, o que dá justificativa **estrutural** (e não apenas
   sintática) para o fator invertido não depender de `l` — o achado da NOTA 2.

---

## 13. Pontos em aberto

1. **Duas hipóteses implícitas** que o artigo não enuncia, só usa:
   - `E[s̄ s̄^H] = β I_r` (H3) — potências desiguais dariam `diag(β_1,...,β_r)`.
   - `E[s s^H] = E_s I_K` (H9) — mesma estrutura, para os UEs-alvo; está embutida na eq. (3).

   Ambas valem ser explicitadas na metodologia do TG, como pontos onde o artigo omite e nós
   tornamos explícito.
2. **Precisão interna não especificada.** `w = 12` é largura de **fronthaul** (`:640`), não do
   datapath. Precisa de sweep de ponto fixo contra SER, no IoT de 20 dB (ver Seção 6.1).
3. **`N_coh` sem valor numérico** no artigo. Junto com H7, determinaria a cadência real de
   `R̂_cc` — hoje só sabemos que é mais folgada que a de `H_c`, sem quantificar.
4. **A eq. (7) no daisy chain.** `[ARTIGO :140]` descreve "collect + broadcast", padrão de
   estrela. No anel isso vira duas voltas, e o artigo não detalha o custo.
5. **Custo de memória de `{n_c^i}`** (Seção 8.3): 3072 números complexos por DU em config A.
   Não está registrado em nenhuma linha do `constraints.csv`.
