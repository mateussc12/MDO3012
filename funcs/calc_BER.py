import numpy as np


def calc_BER(vetor1, vetor2):
    """
    Calcula a BER entre dois vetores binários
    :param vetor1:
    :param vetor2:
    :return: BER
    """

    BER = np.logical_xor(vetor1, vetor2).sum() / np.size(vetor1)

    return BER
