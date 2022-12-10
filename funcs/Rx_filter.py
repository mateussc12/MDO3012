import numpy as np
from scipy import signal


def Cut_repetead(unnormalized_wave_uncut, Ta_signal, Ta_MDO):
    """
    Verifica se existe parte repetida da Rx_Wave, caso haja, corta ela
    :param unnormalized_wave_uncut: Rx_wave não cortada
    :param Ta_signal: Tempo total da onda enviada
    :param Ta_MDO: Tempo total mostrado no MDO
    :return: Rx_Wave cortada
    """
    proporcao = Ta_signal / Ta_MDO
    if proporcao == 1:
        return unnormalized_wave_uncut

    else:
        final = int(len(unnormalized_wave_uncut) * proporcao)
        unnormalized_wave = np.array(unnormalized_wave_uncut[0:final])

        return unnormalized_wave


def Digitalize(signal, NPPS, N_Simb, threshold):
    """
    Filtra os dados obtidos do MDO
    :param unnormalized_wave: Vetor obtido da captura da tela do MDO
    :param NPPS: Pontos por periodo
    :param N_Simb: Numero de simbolos
    :param threshold: Limite a ser filtrado
    :return: A onda binária, com o downsample
    """

    Rx_bin_wave = np.zeros(N_Simb)

    if threshold == 'mean':
        threshold = np.mean(signal)

    for i in range(N_Simb):

        intervalo_media = np.mean(signal[int(i * NPPS):int((i + 1) * NPPS)])

        if np.greater_equal(intervalo_media, threshold):
            Rx_bin_wave[i] = 1

    return Rx_bin_wave


def Eye_treshold(signal):
    """
    Calcula o limiar de decisão baseado no diagrama de olho
    :param normalized_wave: normalized wave
    :return: limiar de decisão
    """
    # Média das amostras
    mean_diagram_position = np.mean(signal)
    # Amostras acima da média
    pos_diagram_position_vector = []
    # Amostras abaixo da média
    neg_diagram_position_vector = []
    for sample in signal:
        if sample >= mean_diagram_position:
            pos_diagram_position_vector.append(sample)
        else:
            neg_diagram_position_vector.append(sample)

    pos_diagram_position = np.mean(pos_diagram_position_vector) - np.std(pos_diagram_position_vector)
    neg_diagram_position = np.mean(neg_diagram_position_vector) + np.std(neg_diagram_position_vector)

    eye_treshold = (pos_diagram_position + neg_diagram_position) / 2

    return eye_treshold
