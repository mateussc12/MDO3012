def horizontal_scale(horizontal_scale):
    """
    Retorna aa escala horizontal possível no MDO, já que ela é limitada em valores específicos
    :param horizontal_scale: Escala horizontal da onda
    :return: escala horizontal do MDO
    """

    if horizontal_scale <= 10e-9:
        horizontal_scale = 10e-9
    elif horizontal_scale <= 20e-9:
        horizontal_scale = 20e-9
    elif horizontal_scale <= 40e-9:
        horizontal_scale = 40e-9
    elif horizontal_scale <= 100e-9:
        horizontal_scale = 100e-9
    elif horizontal_scale <= 200e-9:
        horizontal_scale = 200e-9
    elif horizontal_scale <= 400e-9:
        horizontal_scale = 400e-9
    elif horizontal_scale <= 1000e-9:
        horizontal_scale = 1000e-9
    elif horizontal_scale <= 2000e-9:
        horizontal_scale = 2000e-9
    elif horizontal_scale <= 4000e-9:
        horizontal_scale = 4000e-9
    elif horizontal_scale <= 10e-6:
        horizontal_scale = 10e-6
    elif horizontal_scale <= 20e-6:
        horizontal_scale = 20e-6
    elif horizontal_scale <= 40e-6:
        horizontal_scale = 40e-6
    elif horizontal_scale <= 100e-6:
        horizontal_scale = 100e-6
    elif horizontal_scale <= 200e-6:
        horizontal_scale = 200e-6
    elif horizontal_scale <= 400e-6:
        horizontal_scale = 400e-6
    elif horizontal_scale <= 800e-6:
        horizontal_scale = 800e-6
    elif horizontal_scale <= 1000e-6:
        horizontal_scale = 1000e-6
    elif horizontal_scale <= 2000e-6:
        horizontal_scale = 2000e-6
    elif horizontal_scale <= 4000e-6:
        horizontal_scale = 4000e-6
    elif horizontal_scale <= 10e-3:
        horizontal_scale = 10e-3
    elif horizontal_scale <= 20e-3:
        horizontal_scale = 20e-3
    elif horizontal_scale <= 40e-3:
        horizontal_scale = 40e-3
    elif horizontal_scale <= 100e-3:
        horizontal_scale = 100e-3
    elif horizontal_scale <= 200e-3:
        horizontal_scale = 200e-3
    elif horizontal_scale <= 400e-3:
        horizontal_scale = 400e-3
    elif horizontal_scale <= 400e-3:
        horizontal_scale = 400e-3
    elif horizontal_scale <= 10:
        horizontal_scale = 10

    return horizontal_scale
