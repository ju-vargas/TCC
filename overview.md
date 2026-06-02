### Resumo do trabalho

Massive MU-MIMO (Multi-User Multiple-Input Multiple-Output) é uma tecnologia de comunicação de dados que usa um grande número de antenas para comunicação wireless de dados.

Na recepção de dados vindos do usuário (celular, por exemplo) na estação base (uplink) são realizadas as operações de equalização e detecção. A etapa de equalização realiza cálculos que consideram o modelo do canal (ambiente no qual estão sendo transmitidos os dados) e o ruído de comunicação para estimar os símbolos transmitidos pelos usuários. A etapa de detecção transforma os símbolos recebidos em bits, de acordo com a codificação utilizada.

O sistema de comunicação é descrito pela operação matricial:

$y = Hx + n$

Na equação, $x$ é o vetor de símbolos transmitidos pelos usuários, $y$ é o vetor recebido na antena da estação base, $H$ é a matriz que modela o canal e $n$ é o modelo de ruído selecionado.

O objetivo do cálculo é descobrir o vetor $x$ com a maior fidelidade possível.

Equalizadores lineares alcançam eficiência espectral próxima à do detector de máxima verossimilhança (ML) para a tarefa de equalização de dados, e são formulados da seguinte forma:
$$
\begin{equation*}
\hat{\mathbf{x}}=\underset{\mathbf{x} \in \mathbb{C}^{U}}{\arg \min }\|\mathbf{y}-\mathbf{H} \mathbf{x}\|_{2}^{2}+\rho\|\mathbf{x}\|_{2}^{2} .
\end{equation*}
$$

Para equalização LMMSE, $\rho$ é o ruído normalizado pela potência de transmissão de cada usuário.

A forma fechada desse cálculo, válida sob a hipótese de ruído AWGN (em que a matriz de covariância de ruído é proporcional à identidade), é dada por:
$$\hat{\mathbf{x}}=\left(\mathbf{H}^{H} \mathbf{H}+\rho \mathbf{I}\right)^{-1} \mathbf{H}^{H} \mathbf{y}$$

Para o caso geral com ruído colorido, a formulação do equalizador LMMSE incorpora a matriz de covariância do ruído $\mathbf{R}_n$ e a matriz de covariância do sinal $\mathbf{R}_x$:
$$\hat{\mathbf{x}}=\left(\mathbf{H}^{H} \mathbf{R}_n^{-1} \mathbf{H}+\mathbf{R}_x^{-1}\right)^{-1} \mathbf{H}^{H} \mathbf{R}_n^{-1} \mathbf{y}$$

A complexidade da operação de inversão nesse cálculo cresce com o número de antenas na ordem de $\mathcal{O}(N^3)$. Para sistemas de MIMO Massivo convencionais, centralizados, essa complexidade se torna limitante.

Nos últimos anos surgiram soluções descentralizadas, que dividem o cálculo em clusters de antenas. No entanto, boa parte dessas soluções considera apenas ruído gaussiano branco (AWGN), que pode ser facilmente decomposto entre os diferentes clusters de antena ou, ainda, permite o uso de técnicas de *inversion-avoidance*. Ao considerar outras formas de ruído, como o acoplamento entre antenas (ruído colorido), a decomposição do ruído se torna mais complexa e a supressão da operação de inversão também. Trabalhos recentes apresentam soluções que consideram ruído colorido em arquiteturas MIMO descentralizadas, com inversão de matriz.

Mesmo em arquiteturas descentralizadas, a inversão de matriz ainda tem custo computacional relevante. O trade-off entre a frequência da operação de inversão, relacionado ao tempo no qual o símbolo recebido está disponível no canal, e ao bit-error-rate aceitável no final da detecção é uma diretriz utilizada para selecionar otimizações na operação de inversão, por exemplo, diminuir a precisão nos cálculos. O uso de FPGA ou ASICs na arquitetura descentralizada é adotado ou citado como trabalho futuro em diversos trabalhos relacionados.

Diversas arquiteturas de inversão de matrizes implementadas em FPGA são apresentadas na literatura, como decomposição de Cholesky e série de Neumann. Entretanto, uma análise inserida no contexto da equalização LMMSE descentralizada considerando o ruído colorido proposta em trabalhos recentes ainda não foi explorada.

O trabalho propõe implementar em FPGA o módulo que realiza a operação de inversão de matrizes na equalização LMMSE em sistemas Massive MU-MIMO descentralizados, analisando métricas de qualidade (BER) e de implementação em hardware (número de LUTs e consumo de potência).


### Referências principais

Arquitetura dentro da qual será analizada a inversão: 
X. Zhao, M. Li, B. Wang, E. Song, T. -H. Chang and Q. Shi, "Efficient LMMSE Equalization for Massive MIMO Systems Under Decentralized Baseband Processing Architecture," in IEEE Journal on Selected Areas in Communications, vol. 43, no. 3, pp. 736-751, March 2025, doi: 10.1109/JSAC.2025.3531524.


Justificativo para operações que consideram ruído colorido:
Z. Zhuang, X. Zhang, D. Xu, S. Song and Y. C. Eldar, "Decentralized MIMO Systems With Imperfect CSI Using LMMSE Receivers," in IEEE Journal of Selected Topics in Signal Processing, vol. 19, no. 2, pp. 331-348, March 2025, doi: 10.1109/JSTSP.2025.3539098.

Paper para selecionar métricas de análise:
K. Li et al., "Design Trade-offs for Decentralized Baseband Processing in Massive MU-MIMO Systems," 2019 53rd Asilomar Conference on Signals, Systems, and Computers, Pacific Grove, CA, USA, 2019, pp. 906-912, doi: 10.1109/IEEECONF44664.2019.9048727.


Paper com implementação em FPGA:
K. Li, C. Jeon, J. R. Cavallaro and C. Studer, "Decentralized equalization for massive MU-MIMO on FPGA," 2017 51st Asilomar Conference on Signals, Systems, and Computers, Pacific Grove, CA, USA, 2017, pp. 1532-1536, doi: 10.1109/ACSSC.2017.8335613.