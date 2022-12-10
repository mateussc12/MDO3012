from funcs import MDO_Write_Read, Rx_filter, time2freq, awgn
import numpy as np
from funcs.MDO_horizontal_scale import horizontal_scale
from funcs.eye_diagram import eye_diagram
from funcs.calc_BER import calc_BER
import matplotlib.pyplot as plt
import os
import traceback
from scipy import signal


########################################Parâmetrização##################################################################
visa_address = 'OSCI'

# Limite MDO 2^17 bits
# Número de simbolos
N_Simb = 2 ** 9
# Número de pontos por simbolo
NPPS = 2 ** 5
# Criação do vetor
Tx_bin_wave = np.random.choice([0, 1], N_Simb)
Tx_bin_wave = np.array(Tx_bin_wave)
# ts = Periodo de simbolo
Ts_wave = 5.12e-6

# Simbolo super amostrado
Tx_bin_wave_supersampled = np.repeat(Tx_bin_wave, NPPS)
# Periodo de amostragem da onda inteira
Ta_wave = Ts_wave * NPPS
Fa_wave = 1 / Ta_wave
print(f'Periodo de amostragem (Ta_wave) da onda = {Ta_wave} s')
print(f'Taxa de amostragem (Fa_wave) da onda = {Fa_wave} Hz')
print(f'Quantidade de simbolos = {N_Simb}')
print(f'Superamostragem no código = {NPPS}')
# Nsamp_amostrado = número de dados, já amostrado
Nsamp_amostrado = len(Tx_bin_wave) * NPPS
# td = tempo de dado, já amostrado
td = Ta_wave / Nsamp_amostrado

# Total de amostradas a serem mostradas na tela do MDO
Nsamp_mdo = 100000
# Escala de tempo a ser mostrada na tela do MDO
ta_mdo = horizontal_scale(Ta_wave)
# Downsampling feito pelo mdo
# NPPS_MDO3012 deve NECESSARIAMENTE ser um número inteiro, sem precisar de arredondamentos, caso contrário, haverão erros de sincronismo
NPPS_MDO3012 = np.around((Ta_wave / ta_mdo) * (Nsamp_mdo / len(Tx_bin_wave_supersampled)))
print(f'Superamostragem MDO3012 = {(Ta_wave / ta_mdo) * (Nsamp_mdo / len(Tx_bin_wave_supersampled))}')
NPPS_total = NPPS * NPPS_MDO3012
print(f'Superamostragem total = {NPPS_total}')

# Perido de amostragem de um simbolo
Ta = Ta_wave / N_Simb
Fa = 1 / Ta
print(f'Periodo de amostragem (Ta) por simbolo = {Ta} s')
print(f'Taxa de amostragem (Fa) por simbolo = {Fa} Hz')

SNR = 5
print(f'SNR = {SNR} dB')

########################################################################################################################


#################################################Debug##################################################################
current_dir = os.getcwd()
eye_enable = 1      # Habilita o diagrama de olho
plots = 1           # Habilita os plots
decisao_limiar = 2  # Limiar de filtragem, 0 = 0, 1 = média, 2 = limiar histograma diagrama de olho
########################################################################################################################



##############################################Escrita e leitura de dados################################################
MDO_Write_Read.Write(visa_address, Tx_bin_wave_supersampled, ta=f'period {Ta_wave}', horizontal_scale=f'scale {ta_mdo / 10}',
                     num_points=Nsamp_mdo)

unnormalized_wave_uncut, normalized_wave_uncut, bin_normalized_wave_uncut, t_print_tela, t_acq, t_autoset, t_data = MDO_Write_Read.Read(
    visa_address, channel='CH1')
########################################################################################################################


############################################Filtragem dos dados(Retirada de dados repetidos)############################
unnormalized_wave = Rx_filter.Cut_repetead(unnormalized_wave_uncut, Ta_wave, ta_mdo)
########################################################################################################################

#############################################Canal AWGN#################################################################
# Aplica ruído AWGN
unnormalized_wave_noise = awgn.AWGN_noise(unnormalized_wave, SNR, NPPS_total)
########################################################################################################################

#############################################Recepção###################################################################
# Normaliza o sinal
normalized_wave_noise = unnormalized_wave_noise / np.max(np.abs(unnormalized_wave_noise))
# Faz o downsample no sinal recebido do MDO3012
downsampled_wave = signal.resample(normalized_wave_noise, int(np.size(normalized_wave_noise) / NPPS_MDO3012))
########################################################################################################################

###########################################Diagrama de olho#############################################################
if eye_enable:
    """
    Cria as pastas onde os diagramas de olho serao salvos
    """
    try:
        os.mkdir(os.path.join(current_dir, 'eye_diagram'))
    except FileExistsError:
        pass
    divisao = 0.025

    eye_signal, eye_t = eye_diagram(downsampled_wave, Ta, NPPS)

    fig, (ax, ax1) = plt.subplots(1, 2, sharey=True, width_ratios=[0.8, 0.2], figsize=[12.8, 9.6], layout='tight')
    for eye_period in eye_signal:
        ax.plot(eye_t, np.real(eye_period), color='b', linewidth=0.5)
    counts, bins, patches = ax1.hist(np.real(np.array(eye_signal).flatten()), np.arange(-1, 1.001, divisao),
                                     orientation='horizontal', color='b')
    ax.set_title(f"Diagrama de olho")
    plt.savefig(os.path.join(current_dir, 'eye_diagram', 'eye_diagram'))
    plt.close()
########################################################################################################################


############################################Filtragem dos dados(limiar de decisão)######################################
try:
    if decisao_limiar == 0:
        Rx_bin_wave = Rx_filter.Digitalize(downsampled_wave, NPPS_MDO3012, N_Simb, threshold=0)
    elif decisao_limiar == 1:
        Rx_bin_wave = Rx_filter.Digitalize(downsampled_wave, NPPS_MDO3012, N_Simb, threshold='mean')
    elif decisao_limiar == 2:
        eye_treshold = Rx_filter.Eye_treshold(normalized_wave_noise)
        Rx_bin_wave = Rx_filter.Digitalize(downsampled_wave, NPPS_MDO3012, N_Simb, threshold=eye_treshold)
    else:
        raise ValueError('O valor de decisao_limiar está provavelmente errado')
except ValueError:
    print(traceback.format_exc())
########################################################################################################################
"""
##########################################Equalização###################################################################
#df = pd.read_csv('Dados_Resp_Freq_CPID/Transfer_Function_FFT.csv')
df = pd.read_csv('Dados_Resp_Freq_LABTEL/Transfer_Function_FFT.csv')
Transfer_Function_FFT = np.array(df, dtype=complex)

Rx_bin_wave_FFT = np.fft.fft(Rx_bin_wave)
print(np.size(Rx_bin_wave_FFT))
print(np.size(Transfer_Function_FFT))
Rx_bin_wave_Equalized_FFT = Rx_bin_wave_FFT / Transfer_Function_FFT
Rx_bin_wave_Equalized = np.fft.ifft(Rx_bin_wave_Equalized_FFT)

t = np.linspace(0, Ta, len(Rx_bin_wave))
f = time2freq.time2freq(t)
"""
########################################################################################################################


#########################################Calcula a BER##################################################################
BER = calc_BER(Tx_bin_wave, Rx_bin_wave)
print(f'BER = {BER}')
"""
##########################################Equalização###################################################################
#BER = calc_BER(Tx_bin_wave, Rx_bin_wave_Equalized)
#print(f'BER com equalizacao = {BER}')
"""
########################################################################################################################


####################################################Plotagens###########################################################
if plots:
    """
    Cria as pastas onde os diagramas de olho serao salvos
    """
    try:
        os.mkdir(os.path.join(current_dir, 'plots'))
    except FileExistsError:
        pass

    t = np.linspace(0, Ta_wave, len(Rx_bin_wave))

    fig, (ax, ax1, ax2, ax3) = plt.subplots(4, 1, figsize=[12.8, 9.6], layout='tight')
    ax.plot(unnormalized_wave, label='Saída do MDO')
    ax1.plot(unnormalized_wave_noise, label='Saída do MDO com AWGN')
    ax2.plot(normalized_wave_noise, label='Saída do MDO com AWGN normalizada')
    ax3.plot(downsampled_wave, label='Onda já normalizada com downsample')
    fig.suptitle("Dados antes e depois da filtragem")
    ax.set_xlim([0, int(20*NPPS_total)])
    ax1.set_xlim([0, int(20*NPPS_total)])
    ax2.set_xlim([0, int(20*NPPS_total)])
    ax2.set_ylim([-1, 1])
    ax3.set_xlim([0, int(20*NPPS)])
    ax3.set_ylim([-1, 1])
    ax.legend()
    ax1.legend()
    ax2.legend()
    ax3.legend()
    plt.savefig(os.path.join(current_dir, 'plots', 'Antes_Depois_filtragem'))
    plt.close()

    fig, (ax, ax1) = plt.subplots(2, 1, figsize=[12.8, 9.6], layout='tight')
    ax.plot(Tx_bin_wave, color='r', label='Tx wave')
    ax1.plot(Rx_bin_wave, label='Rx wave')
    fig.suptitle("Dados recebidos e enviados")
    ax.legend(loc=7)
    ax1.legend(loc=7)
    plt.savefig(os.path.join(current_dir, 'plots', 'subplot_Tx_Rx_bin'))
    plt.close()

    if decisao_limiar == 2:
        plt.figure(figsize=[12.8, 9.6], layout='tight')
        plt.plot(downsampled_wave)
        plt.plot(np.zeros(np.size(downsampled_wave)), label='0')
        mean = np.mean(downsampled_wave)
        plt.plot(np.repeat(mean, np.size(downsampled_wave)), label=f'mean = {np.round(mean, 5)}', linewidth=3)
        plt.plot(np.repeat(eye_treshold, np.size(downsampled_wave)), label=f'eye_treshold = {np.round(eye_treshold, 5)}')
        plt.title("Comparação entre os niveis de decisão")
        plt.legend(loc=1)
        plt.ylim([-0.25, 0.25])
        plt.savefig(os.path.join(current_dir, 'plots', 'treshold'))
        plt.close()
    """
    ##########################################Plot de Equalização###########################################################
    fig, (ax2, ax3) = plt.subplots(2, 1)
    ax2.plot(t, Tx_bin_wave_supersampled, color='r', label='Tx wave')
    ax3.plot(t, Rx_bin_wave_Equalized, label='Rx wave Equalizada')
    fig.suptitle("Dados recebidos e enviados com equalizacao")
    ax.legend(loc=7)
    ax1.legend(loc=7)
    fig.savefig('img\subplot_Tx_Rx_bin_Equalized.png')
    
    plt.figure()
    plt.plot(f, Transfer_Function_FFT, label='Tranfer function')
    plt.title("Funcao de transferencia do sistema")
    plt.legend(loc=7)
    plt.savefig('img\Transfer_function.png')
    """
########################################################################################################################
