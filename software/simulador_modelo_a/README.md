# Simulador modelo A

Cópia de `../simulador` em que a covariância do ruído é estimada pela **média em
frequência**, como diz a nota 4 de Zhao et al. (`../simulador/referencias/zhao2025_jsac/paper.md:821`).
O simulador original segue a Seção VI do artigo (`paper.md:577`): a covariância é a do
próprio PRB (modelo B).

| | Modelo A (este simulador) | Modelo B (artigo, Seção VI) |
| :-- | :-- | :-- |
| Canal | `H_f`, `H̄_f` em 64 PRBs ao longo de 100 MHz | um único PRB |
| Amostras de estimação | 192, espalhadas na banda (PRB `i mod 64`) | 192, todas do PRB equalizado |
| `R̂` | uma por realização, a mesma para todos os PRBs | uma por PRB |
| Ruído dos dados | covariância do próprio PRB | covariância do próprio PRB |

Os dois modelos rodam sobre os mesmos canais (`--model AB`, padrão), então a diferença
entre eles vem só do modelo de covariância.

## O que mudou em relação a `../simulador`

- `quadriga/export_quadriga_channels.m`: mesmos sorteios (cenário, fc, arranjo, sementes),
  mas a resposta em frequência é tirada em 64 pontos sobre 100 MHz. O ponto 0 é f0,
  igual ao export original; `convert_quadriga_export.py` confere isso.
- `dbp_sim/m2_channel.py`: backends de canal na banda (`QuaDriGaBandFileChannel`,
  `StandInULABandChannel`) e normalização por UE com a potência média na banda.
- `dbp_sim/m5_noise.py`: ruído sorteado por PRB, `β` pela média na banda, distribuição
  das amostras de estimação e o diagnóstico de dimensões de interferência.
- `dbp_sim/m1_driver.py`: `run_panel_band`, o laço do modelo A (e do B sobre os mesmos canais).
- `dbp_sim/m7_equalizers.py`: no BCD-MMSE, `G_c = E_s H_c H_c^H + R̂_cc` é invertida uma
  vez por DU e reaproveitada nas iterações. O resultado não muda; só o número de chamadas.
- `dbp_sim/params.py`: parâmetros novos com proveniência (`covariance_model`,
  `bandwidth_hz`, `n_carriers`, `estimation_spread`, `n_eval_prbs`).
- `run_modelo_a.py`: ponto de entrada. Por padrão roda LMMSE, ZF e BCD-MMSE com 1 a 4 iterações.
- `test_dbp_sim.py`: verificações originais e as seções 9 e 10 (modelo A).

`dados/channels_quadriga_M*_K*_r*.npz` são cópias dos canais de uma subportadora do
simulador original; servem aos testes originais e à conferência do export.

## Como rodar

O MATLAB usa o servidor de licença `matlab.ufrgs.br`, então precisa da rede da UFRGS ou da VPN.

```sh
cd quadriga && matlab -nodisplay -nosplash -r export_quadriga_channels   # ~15 min
cd .. && ../simulador/.venv/bin/python quadriga/convert_quadriga_export.py

../simulador/.venv/bin/python test_dbp_sim.py                 # verificações
../simulador/.venv/bin/python run_modelo_a.py --quick --panels a
../simulador/.venv/bin/python run_modelo_a.py --panels a      # modelos A e B, painel (a)
../simulador/.venv/bin/python run_modelo_a.py --provenance    # tabela de proveniência
```

Sem os canais do QuaDRiGa, `--channel standin_ula` usa um canal substituto (não é o do artigo).

## Escolhas que não vêm do artigo

- Banda de 100 MHz: limite superior da banda média do NR (Lin e Lee, *5G and Beyond*, cap. 1).
  A Tabela I do artigo implica 120 kHz e 275 PRBs (FR2), o que não combina com fc = 3,5 GHz.
- 64 PRBs amostrados, a cada 1,5625 MHz, para os arquivos ficarem pequenos.
- Amostras de estimação em rodízio pelos PRBs (3 por PRB).
- 8 PRBs avaliados por realização.
- A média é só em frequência. Não há média no tempo (T_R): cada realização é um instante.
