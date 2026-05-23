import scipy.io as sio
import numpy as np

data = sio.loadmat('../channels_fig8a_M128_C8_K8.mat')
H = data['H_tgt_all']
print("H shape:", H.shape)
col_pow = np.sum(np.abs(H[:, 0, 0])**2)
print("col 0 pow:", col_pow)
