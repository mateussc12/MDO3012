import numpy as np


def Power_measure(Signal):
    """
    Calcula a potência de um sinal discreto
    Px=limN→∞(1/(2N + 1)) * Somatório_n de -N a N do |x[n]|²
    :param Signal: Sinal a ter sua potência calculada
    :return: Power
    """
    Power = np.sum(np.power(np.abs(Signal), 2)) / len(Signal)

    return Power
