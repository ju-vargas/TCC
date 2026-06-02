## Maximum Ration Combining

Maximum Ratio Combining (MRC) is a linear diversity technique used in wireless communication to maximize the combined output Signal-to-Noise Ratio (SNR). It works by weighting multiple received signals proportionally to their individual channel strength and correcting for phase shifts, ensuring they add up constructively.How Maximum Ratio Combining WorksMRC is a significant upgrade from Selection Combining (which simply discards weaker signals) or Equal-Gain Combining. To achieve the optimal combined signal, MRC applies the following steps to each branch or antenna:Phase Adjustment (Co-phasing): Each signal is multiplied by the complex conjugate of its channel's fading coefficient. This eliminates the phase shifts caused by the environment, aligning the signals in phase so they add constructively instead of canceling each other out.Weighting by Signal Strength: The signals are then scaled (weighted) proportionally to their signal-to-noise ratio. Signals from channels with high fading/noise are suppressed, while channels with strong, clear signals are heavily favored.Summation: All adjusted branches are combined into a single signal


### BBU
Baseband Processing Unit

### CHEST
Local Channel Estimation 
Calcula CSI (Chanel State Information)

### $N_{coh}$
is the maximum amount of consecutive symbols that a receiver can process while assuming the channel's transmission characteristics (like amplitude and phase) are constant.

#### What is Channel Coherence $(N_{\text{coh}})$?
In any digital transmission, wireless channels (due to fading, mobility, and multipath propagation) don't stay perfectly identical.

#### Definition: 
$(N_{\text{coh}})$ is the maximum amount of consecutive symbols that a receiver can process while assuming the channel's transmission characteristics (like amplitude and phase) are constant.

#### How it's used: 
Instead of calculating complex mathematical formulas (like equalization or channel estimation matrices) for every single symbol, processors use a single calculation that they can safely reuse across $(N_{\text{coh}})$ consecutive symbols. 

#### Why $(N_{\text{coh}})$ is Important

* Resource Allocation: 
To estimate how the channel is behaving, transmitters send a short sequence of known reference data (called pilot symbols). Once the channel is estimated, the rest of the symbols in that $(N_{\text{coh}})$ time block are used for actual data transmission.

* Speed and Efficiency: 
Systems with large coherence intervals require fewer pilot sequences, which vastly increases the data payload efficiency (throughput).

* Doppler Shift:
$(N_{\text{coh}})$ is directly linked to the speed of the objects communicating. Fast-moving devices or cars result in rapidly changing channels, which yield a much smaller $(N_{\text{coh}})$. Slower, stationary devices yield a much larger $(N_{\text{coh}})$.

#### Mathematical Context 
$(N_{\text{coh}})$ helps define the block-fading nature of wireless channels (like in MIMO or massive MIMO networks). A common block-fading mathematical model holds that within a total block size of $(N)$ transmitted symbols, $(N)$ must remain less than or equal to $(N_{\text{coh}})$ for the transmission to be accurate.Equation Example:If the channel coherence time is $(T_{\text{coh}})$ and the symbol duration is $(T_{s})$, the coherence length in symbols can be calculated as:$(N_{\text{coh}} = \frac{T_{\text{coh}}}{T_s})$