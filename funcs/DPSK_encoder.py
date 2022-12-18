import numpy as np


def DPSK_encoder(data, pre_bit=1):
    """
    Encoder DPSK (XNOR)
    :param data:
    :param pre_bit:
    :return:
    """

    encoded_data = []

    for bit in data:
        DPSK_cod = np.logical_not(np.logical_xor(bit, pre_bit))
        encoded_data.append(DPSK_cod)

        pre_bit = DPSK_cod

    return np.array(encoded_data, dtype=int)
