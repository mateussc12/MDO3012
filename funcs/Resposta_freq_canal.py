from funcs import MDO_Write_Read
import numpy as np
from funcs.MDO_horizontal_scale import horizontal_scale
import Rx_filter
import matplotlib.pyplot as plt
from time2freq import time2freq
from scipy import signal
from funcs.Power_measure import Power_measure

np.set_printoptions(threshold=np.inf)

########################################Parâmetrização###############################################
visa_address = 'OSCI'
# Limite MDO 2^17 bits

# Número de simbolos
Nsamp = 2**9
# Criação do vetor
Tx_bin_wave = np.zeros(Nsamp)
mid = int(len(Tx_bin_wave)/2)
Tx_bin_wave[mid-2:mid+2] = 1


# ts = Periodo de simbolo
ts = 5.12e-6
oversample = 2 ** 5


# Simbolo super amostrado
Tx_bin_wave_supersampled = np.repeat(Tx_bin_wave, oversample)
# ta = Periodo de simbolo, já amostrado
ta = ts * oversample
print(f'Periodo de amostragem (ta) = {ta}')
# Nsamp_amostrado = número de dados, já amostrado
Nsamp_amostrado = len(Tx_bin_wave) * oversample
# td = tempo de dado, já amostrado
td = ta / Nsamp_amostrado


# Total de amostradas a serem mostradas na tela do MDO
Nsamp_mdo = 100000
ta_mdo = horizontal_scale(ta)
# Downsampling feito pelo mdo
n_down = np.around((ta / ta_mdo) * (Nsamp_mdo / len(Tx_bin_wave)))
print((ta / ta_mdo) * (Nsamp_mdo / len(Tx_bin_wave)))
########################################################################################################################


##############################################Escrita e leitura de dados################################################
MDO_Write_Read.Write(visa_address, Tx_bin_wave_supersampled, ta=f'period {ta}', horizontal_scale=f'scale {ta_mdo / 10}',
                     num_points=Nsamp_mdo)

unnormalized_wave_uncut, normalized_wave_uncut, bin_normalized_wave_uncut, t_print_tela, t_acq, t_autoset, t_data = MDO_Write_Read.Read(
    visa_address, channel='CH1')
########################################################################################################################


############################################Filtragem dos dados(Retirada de dados repetidos)############################
Rx_unnormalized_wave = Rx_filter.Cut_repetead(unnormalized_wave_uncut, ta, ta_mdo)
print(f'Tamanho vetor repetido {len(unnormalized_wave_uncut)}')
print(f'Tamanho vetor util {len(Rx_unnormalized_wave)}')
########################################################################################################################


#########################################Calculos para as plotagens#####################################################
#FFT Tx
Tx_power = Power_measure(Tx_bin_wave_supersampled)
print(f'Potência Tx: {Tx_power}')

Tx_FFT = np.fft.fft(Tx_bin_wave_supersampled)
#np.savetxt('Dados_Resp_Freq_CPID\Tx_bin_wave_supersampled.csv', Tx_bin_wave_supersampled, delimiter=',')
np.savetxt('Dados_Resp_Freq_Labtel\Tx_bin_wave_supersampled.csv', Tx_bin_wave_supersampled, delimiter=',')
#np.savetxt('Dados_Resp_Freq_CPID\Tx_FFT.csv', Tx_FFT, delimiter=',')
np.savetxt('Dados_Resp_Freq_Labtel\Tx_FFT.csv', Tx_FFT, delimiter=',')
t_Tx = np.linspace(0, ta, int(ta/td))
f_Tx = time2freq(t_Tx)

#FFT Rx
#Rx_unnormalized_wave = Rx_unnormalized_wave / np.max(np.abs(Rx_unnormalized_wave))
Rx_power = Power_measure(Rx_unnormalized_wave)
print(f'Potência Rx: {Rx_power}')

Rx_unnormalized_FFT = np.fft.fft(Rx_unnormalized_wave)
#np.savetxt('Dados_Resp_Freq_CPID\RX_unnormalized_wave.csv', Rx_unnormalized_wave, delimiter=',')
np.savetxt('Dados_Resp_Freq_Labtel\RX_unnormalized_wave.csv', Rx_unnormalized_wave, delimiter=',')
#np.savetxt('Dados_Resp_Freq_CPID\RX_unnormalized_wave_FFT.csv', Rx_unnormalized_FFT, delimiter=',')
np.savetxt('Dados_Resp_Freq_Labtel\RX_unnormalized_wave_FFT.csv', Rx_unnormalized_FFT, delimiter=',')
t_Rx = np.linspace(0, ta, int(len(Rx_unnormalized_FFT)))
f_Rx = time2freq(t_Rx)

#Func de transferencia
#Fazendo Tx e Rx e terem os mesmo tamanho
Tx_resampled = signal.resample(Tx_bin_wave_supersampled, len(Rx_unnormalized_wave))
Tx_resampled_power = Power_measure(Tx_resampled)
print(f'Potência Tx superamostrado: {Tx_resampled_power}')

Tx_resampled_FFT = np.fft.fft(Tx_resampled)

t_Transfer_Function = t_Rx
f_Transfer_Function = f_Rx
Tx_resampled_FFT[np.abs(Tx_resampled_FFT) == 0] = -1e-12-1e-12j
Transfer_Function_FFT = Rx_unnormalized_FFT / Tx_resampled_FFT
print(max(Transfer_Function_FFT))
print(min(Transfer_Function_FFT))
#np.savetxt('Dados_Resp_Freq_CPID\Transfer_Function_FFT.csv', Transfer_Function_FFT, delimiter=',')
np.savetxt('Dados_Resp_Freq_Labtel\Transfer_Function_FFT.csv', Transfer_Function_FFT, delimiter=',')

Transfer_Function = np.fft.ifft(Transfer_Function_FFT)
np.savetxt('Dados_Resp_Freq_Labtel\Transfer_Function.csv', Transfer_Function, delimiter=',')
#np.savetxt('Dados_Resp_Freq_CPID\Transfer_Function.csv', Transfer_Function, delimiter=',')
########################################################################################################################


############################################ Plotagem ##################################################################
fig, (ax, ax1) = plt.subplots(2, 1)
ax.plot(t_Tx, Tx_bin_wave_supersampled, color='r')
ax1.plot(f_Tx, 10*np.log10(np.abs(np.fft.fftshift(Tx_FFT / len(Tx_FFT)))), label='FFT Tx')
ax.set_title("Tx no Tempo")
ax1.set_title("FFT Tx em dB")


fig1, (ax2, ax3) = plt.subplots(2, 1)
ax2.plot(t_Rx, Rx_unnormalized_wave, color='r')
ax3.plot(f_Rx, 10 * np.log10(np.abs(np.fft.fftshift(Rx_unnormalized_FFT / len(Rx_unnormalized_FFT)))))
ax2.set_title("Rx no Tempo")
ax3.set_title("FFT Rx em dB")


fig2, (ax4, ax5) = plt.subplots(2, 1)
ax4.plot(t_Transfer_Function, np.abs(Transfer_Function), color='r')
ax5.plot(f_Transfer_Function, 10*np.log10(np.abs(np.fft.fftshift(Transfer_Function_FFT / len(Transfer_Function_FFT)))))
ax4.set_title("Função de transferência no Tempo")
ax5.set_title("FFT Função de transferência em dB")


plt.tight_layout()
plt.show()
########################################################################################################################
