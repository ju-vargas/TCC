# Diagramas — equalizador BCD-MMSE em daisy chain

Fluxogramas em PlantUML que dão forma visual ao mapeamento de requisitos de
tempo do módulo de inversão de matrizes.

**Fonte da verdade:** `../Efficient_LMMSE_Equalization_..._Archit.md/paper.md`
(Zhao et al., IEEE JSAC vol. 43, 2025 — DOI 10.1109/JSAC.2025.3531524).
**Escopo:** arquitetura *daisy chain* apenas. Estrela, sDR-MMSE, cDR-MMSE e a
variante BCD-MMSE (LRD) estão fora de escopo.

## Os arquivos

| Arquivo | Tipo | O que mostra |
|---|---|---|
| `fases.puml` | atividade | As duas fases (formulação e filtragem), suas entradas, cadências e orçamentos; por que diferem por exatamente 12 |
| `algoritmo3.puml` | atividade | O Algoritmo 3 **transcrito fielmente** (`paper.md:407-436`), sem reordenação, com os três rótulos de bloco do próprio artigo |
| `algoritmo3_hardware.puml` | atividade | **Derivação nossa:** o mesmo algoritmo com a inversão içada para fora do laço BCD, justificada pela ausência do índice `l` na eq. (30) |
| `anel_formulacao.puml` | sequência | O percurso hop a hop da fase de formulação: o que cada DU calcula, o que passa adiante, e o enlace que fecha o anel |
| `anel_filtragem.puml` | sequência | O percurso da fase de filtragem: acumulação de `W_c y_c` até o único DU ligado ao decodificador |
| `anel_pipeline.puml` | sequência | **Derivação nossa:** por que a latência alta do daisy chain é profundidade de pipeline e não gargalo de vazão |
| `modelo_ruido.puml` | grafo de derivação | Do modelo estatístico ao silício: como as hipóteses H1–H9 produzem `G_c`, a matriz que o módulo fatora |

## Ordem de leitura sugerida

0. `modelo_ruido.puml` — de onde vem a matriz a ser invertida (o "por quê")
1. `fases.puml` — o panorama e os dois orçamentos
2. `algoritmo3.puml` — onde as fases aparecem no pseudocódigo
3. `anel_formulacao.puml` — como a formulação percorre o anel
4. `algoritmo3_hardware.puml` — a consequência de projeto
5. `anel_filtragem.puml` — a outra fase, para contraste
6. `anel_pipeline.puml` — por que os orçamentos são de vazão, não de latência

## Convenções

- `[ARTIGO :NNN]` — afirmação do artigo, com o número da linha em `paper.md`.
- `[NOSSO]` — derivação nossa, **não** está no artigo. Precisa ser apresentada
  como tal na defesa.
- As fórmulas do artigo estão em LaTeX; nos diagramas foram transliteradas para
  ASCII (`W_c^l`, `A_{c-1}^l`, `SOMA_c`, `^H`, `^-1`). O **conteúdo** é fiel —
  confira pelos números de linha. Mesma ressalva do
  `../fases_formulacao_vs_filtragem.md`.

## Como renderizar

```bash
plantuml -charset UTF-8 -failfast2 -tpng *.puml    # PNG
plantuml -charset UTF-8 -failfast2 -tsvg *.puml    # SVG (melhor para o TG)
plantuml -charset UTF-8 -failfast2 -teps *.puml    # EPS (LaTeX)
```

Use sempre `-failfast2`. Verificado nesta versão: com erro de sintaxe, o
PlantUML sai com código diferente de zero (com ou sem a flag), mas um arquivo
**truncado — sem `@enduml`** — renderiza em silêncio e sai com código 0.
Se automatizar o build, cheque também que cada arquivo termina em `@enduml`.

Versão usada na validação: PlantUML 1.2020.02. Nessa versão `!theme plain`
**não** existe — por isso os diagramas trazem `skinparam` explícitos.

## Documentos irmãos

- `../constraints.csv` — o mapa de restrições (deliverable principal)
- `../fases_formulacao_vs_filtragem.md` — trilha de evidências com os excertos
  literais do artigo e seus números de linha
- `../modelo_ruido_e_hipoteses.md` — o modelo de ruído e covariância, as hipóteses
  H1–H9 do artigo com suas justificativas, e a anatomia dos inputs do Algoritmo 3
  (`modelo_ruido.puml` é a seção 10 desse documento em forma de diagrama)
