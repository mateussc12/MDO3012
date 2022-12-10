import numpy as np


def eye_diagram(signal, Ts, NPPS):
    """
    Plota o diagrama de olho da onda, ou seja:
    (segunda metade do primeiro periodo -> segundo periodo -> primeira metade do terceiro periodo)
    :param signal: Sinal a ser analisado
    :param Ts: Periodo de simbolo
    :param NPPS: Número de pontos por simbolo
    :return: Vetor contendo os valores, Vetor tempo
    """
    eye_t = np.linspace(0, 2 * Ts, int(2 * NPPS))

    eye_signal = []
    primeiro_ciclo = signal[int(NPPS / 2):int((2 * NPPS + NPPS / 2))]
    eye_signal.append(primeiro_ciclo)
    loop_start = int(2 * NPPS + NPPS / 2)

    cont = 0
    cond = True
    while cond:
        aux = int(loop_start + (cont * (2 * NPPS)))
        aux1 = int(loop_start + ((cont + 1) * (2 * NPPS)))

        cont += 1
        if aux1 >= len(signal):
            cond = False
        else:
            eye_signal.append(signal[aux:aux1])

    return eye_signal, eye_t
