import numpy as np
from numpy.random import standard_normal


def AWGN_noise(signal, SNR_dB, NPPS):
    """
    Adciona ruído AWGN ao sinal
    Eq retirado -> https://www.gaussianwaves.com/2015/06/how-to-generate-awgn-noise-in-matlaboctave-without-using-in-built-awgn-function/
    :param signal: Sinal
    :param SNR_dB: Relação sinal-ruído em dB
    :param NPPS: Numero de pontos por simbolo
    :return: Sinal somado ao ruído AWGN
    """

    signal_power = NPPS * np.sum(np.abs(signal) ** 2) / len(signal)

    SNR_linear = 10 ** (float(SNR_dB) / 10)  # SNR to linear scale

    N0 = signal_power / SNR_linear

    AWGN_noise = np.sqrt(N0 / 2) * (standard_normal(signal.shape))

    return signal + AWGN_noise
