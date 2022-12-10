import statistics
import numpy as np


def time2freq(T):
    """
    Converte o vetor tempo em frequencia
    :param T: Vetor tempo
    :return: Vetor frequencia
    """

    dT = statistics.mean(np.diff(T))
    nT = len(T)
    nT2 = nT/2
    df = 1/(dT*nT)
    return df*(np.arange(-nT2, nT2))
