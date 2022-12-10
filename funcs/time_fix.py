import numpy as np


def sync_time(Tx_reference, Rx_reference):
    aux = np.array([0, 1, 0])
    # rx_aux = np.concatenate((aux, Rx_reference))
    rx_aux = Rx_reference[1::]

    return rx_aux

