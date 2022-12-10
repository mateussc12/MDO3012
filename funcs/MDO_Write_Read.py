"""
Funções para escrever e ler dados do Oscilcópio da série MDO da Tektronics
"""
import time
import pyvisa as visa  # https://github.com/pyvisa/pyvisa
import numpy as np


def Write(visa_address, values, encod='binary', num_points=1000, afg_type='ARBITRARY', impedance='impedance Fifty',
          high='highlevel 2', low='lowlevel -2', ta='period 1.6e-6', state='state ON',
          horizontal_scale='scale 0.16e-6', reference_channel='ch2:', reference_channel_impedance='TERmination FIFty',
          reference_channel_scale='scale 500e-3', reference_channel_position='position 2',
          reference_channel_coupling='COUPLING DC', reference_channel_state='on', channel='ch1:',
          channel_impedance='TERmination fifty', channel_scale='scale 500e-3', channel_position='position -2',
          channel_coupling='COUPLING DC', channel_state='on', trigger_type='type edge', trigger_class='class timeout',
          trigger_time='timeout:time 0.6e-6', horitontal_position='position 0'):
    """
    Escreve uma onda no osciloscópio da série MDO da Tektronics
    :param visa_address: Nome do osciloscópio configurado no VISA
    :param values: Valores a serém escritos (devem estar entre [-1, 1], pois são proporções de high e low)
    :param encod: ASCII ou binário
    :param afg_type: Tipo de onda a ser escrita, ex: ARBITRARY
    :param impedance: Impedância seledionada
    :param high: Valor de tensão alto
    :param low: Valor de tensão baixo
    :param ta: Periodo de amostragem do sinal passado ao MDO
    :param state: Estado de print, ligado ou desligado
    :param horizontal_scale: Escala horizontal
    :param reference_channel: Canal de referência selecionado
    :param reference_channel_impedance: Impedância do canal de referencia
    :param reference_channel_scale: Escala do canal de referência selecionado
    :param reference_channel_position: Posição do trigger no canal de referência selecionado
    :param reference_channel_coupling: Tipo de acoplamento, AC ou DC
    :param reference_channel_state: Liga/desliga o canal de referencia
    :param channel: Canal selecionado
    :param channel_impedance: Impedância do canal
    :param channel_scale: Escala do canal selecionado
    :param channel_position: Posição do trigger no canal selecionado
    :param channel_coupling: Tipo de acoplamento, AC ou DC
    :param channel_state: Liga/desliga o canal
    :param trigger_type: Tipo do trigger
    :param trigger_class: Classe do trigger
    :param trigger_time: Tempo do trigger
    :param horitontal_position: Posição do tempo horizontal, (Delay)
    :return: t_reset = tempo necessário para o rest, t_config = tempo necessário para a configuração do AFG,...
    ...t_print = tempo necessário para a configuração de como os dados serão printados
    """
    "Formata o array numpy para o que o MDO consiga interpretar"
    values_aux = str(list(np.array(values)))
    values = values_aux[1:-1]
    "Comunicação com o instrumento, inicialização"
    rm = visa.ResourceManager()
    scope = rm.open_resource(visa_address)
    scope.timeout = 10000  # ms
    scope.encoding = 'latin_1'
    scope.read_termination = '\n'
    scope.write_termination = None
    scope.write('*cls')  # clear ESR
    scope.write('header OFF')

    print("\n###################################################################")
    print('Iniciando processo de escrita')
    print(scope.query('*idn?'))

    "Reseta o osciloscópio, por boas práticas, além  disso mede o tempo necessário para tal"
    scope.write('*rst')  # reset
    t1_reset = time.perf_counter()
    r = scope.query('*opc?')  # sync
    t2_reset = time.perf_counter()
    t_reset = t2_reset - t1_reset

    "Configura o AFG, com as caracteriscas desejadas, além  disso mede o tempo necessário para tal"
    t1_config = time.perf_counter()

    # Confgigura o tipo de encond, ASCII ou binário
    string_encod = 'afg:arbitrary:emem:points:encdg ' + encod
    scope.write(string_encod)

    # Configura a impedância
    inpedance_string = 'afg:output:load:' + impedance
    scope.write(inpedance_string)

    # Escreve os pontos
    scope.write(f'HORizontal:RECOrdlength {num_points}')
    scope.write(f'afg:arbitrary:emem:points {values}')

    # Configura o tipo de AFG
    afg_type_string = 'afg:function ' + afg_type
    scope.write(afg_type_string)


    # Congfigura o valor alto da tensão
    high_string = 'afg:' + high
    scope.write(high_string)

    # Configura o valor baixo da tensão
    low_string = 'afg:' + low
    scope.write(low_string)

    # Configura o periodo de amostragem do sinal passado ao MDO
    ta_string = 'afg:' + ta
    scope.write(ta_string)  # ta = 1/fa

    # Permite que a tela seja printada
    state_string = 'afg:output:' + state
    scope.write(state_string)

    t2_config = time.perf_counter()
    t_config = t2_config - t1_config

    "Define como a onda deve ser printada na tela, além  disso mede o tempo necessário para tal"
    t1_print = time.perf_counter()

    # Configura a escala horizontal
    horizontal_scale_string = 'horizontal:' + horizontal_scale
    scope.write(horizontal_scale_string)

    # Seleciona a referencia e o canal, configura a escala, posição do trigger e tipo de acoplamento
    string_reference_channel_impedance = reference_channel + reference_channel_impedance
    scope.write(string_reference_channel_impedance)
    string_reference_channel_scale = reference_channel + reference_channel_scale
    scope.write(string_reference_channel_scale)
    string_reference_channel_position = reference_channel + reference_channel_position
    scope.write(string_reference_channel_position)
    string_reference_channel_coupling = reference_channel + reference_channel_coupling
    scope.write(string_reference_channel_coupling)
    string_reference_channel_state = 'Select:' + reference_channel[0:-1] + ' ' + reference_channel_state
    scope.write(string_reference_channel_state)

    string_channel_impedance = channel + channel_impedance
    scope.write(string_channel_impedance)
    string_channel_scale = channel + channel_scale
    scope.write(string_channel_scale)
    string_channel_position = channel + channel_position
    scope.write(string_channel_position)
    string_channel_coupling = channel + channel_coupling
    scope.write(string_channel_coupling)
    string_channel_state = 'Select:' + channel[0:-1] + ' ' + channel_state
    scope.write(string_channel_state)
    #scope.write('CH1:INVert ON')



    # Configura o trigger
    string_trigger = 'trigger:a:'
    string_trigger_type = string_trigger + trigger_type
    scope.write(string_trigger_type)
    scope.write('AUXOUT:SOURCE AFG')
    scope.write('TRIGGER:A:EDGE:SOURCE AUX')
    scope.write('TRIGger:A:LEVel:AUXin 0.5')
    scope.write('TRIGger:A:EDGE:SLOpe rise')

    if trigger_type == 'pulse':
        string_trigger_class = string_trigger + trigger_class
        scope.write(string_trigger_class)
        string_trigger_time = string_trigger + trigger_time
        scope.write(string_trigger_time)

    # Posição do delay horizontal
    scope.write('Horizontal:delay:mode off')
    scope.write('Horizontal:' + horitontal_position)
    
    t2_print = time.perf_counter()
    t_print = t2_print - t1_print

    'Verifica se houveram erros, caso sim, mostra quais flags foram levantadas'
    r = int(scope.query('*esr?'))
    print('event status register: 0b{:08b}'.format(r))
    r = scope.query('allev?').strip()
    print('all event messages: {}\n'.format(r))
    print("Finalizado processo de escrita")
    print("###################################################################")

    return t_reset, t_config, t_print


def Read(visa_address, reset=False, channel='CH1', coupling='coupling dc', horitontal_position='position 0', autoset=False, encod='SRIBINARY'):
    """
    Lê os dados que aparecem na tela do osciloscópio da série MDO da Tektronics
    :param visa_address: Nome do osciloscópio configurado no VISA
    :param reset: Define se o osciloscópio será ou não resetado antes da leitura ser feita
    :param channel: Definal qual canal será lido
    :param coupling: Define o tipo de acoplamento, AC ou DC
    :param horitontal_position: Define a posição do tempo horizontal, (Delay)
    :param autoset: Define se quer-se que o próprio MDO ajuste como a onda aparece na tela
    :param encod: Tipo de codificação
    :return:
    """
    

    "Comunicação com o instrumento, inicialização"
    rm = visa.ResourceManager()
    scope = rm.open_resource(visa_address)
    scope.timeout = 10000  # ms
    scope.encoding = 'latin_1'
    scope.read_termination = '\n'
    scope.write_termination = None
    scope.write('*cls')  # clear ESR

    print("\n###################################################################")
    print('Iniciando processo de leitura')
    print(scope.query('*idn?'))


    if reset is True:
        "Reseta o osciloscópio, por boas práticas, além  disso mede o tempo necessário para tal"
        scope.write('*rst')  # reset
        t1_reset = time.perf_counter()
        r = scope.query('*opc?')  # sync
        t2_reset = time.perf_counter()
        t_reset = t2_reset - t1_reset


    "Configurações quanto os dados a serem printados na tela do MDO, além  disso mede o tempo necessário para tal"
    t1_print_tela = time.perf_counter()

    # Tipo de acoplamento, AC ou DC
    string_channel_coupling = channel + ':' + coupling
    scope.write(string_channel_coupling)

    # Posição do delay horizontal
    scope.write('Horizontal:delay:mode off')
    scope.write('Horizontal:' + horitontal_position)

    if autoset is True:
        scope.write('autoset EXECUTE')  # autoset
    
    t2_print_tela = time.perf_counter()
    t_print_tela = t2_print_tela - t1_print_tela


    "Verifica se existe alguma outra tarefa rodando no MDO"
    t1_autoset = time.perf_counter()
    r = scope.query('*opc?')  # sync
    t2_autoset = time.perf_counter()
    t_autoset = t2_autoset - t1_autoset


    "Configura o IO"
    scope.write('header 0')
    # Tipo de codificação
    scope.write('data:encdg ' + encod)
    # Canal a ser lido
    scope.write('data:source ' + channel)  # channel
    scope.write('data:start 1')  # first sample
    record_length = int(scope.query('horizontal:recordlength?'))
    scope.write('data:stop {}'.format(record_length))  # last sample
    scope.write('wfmoutpre:byt_n 1')  # 1 byte per sample


    "Configura quanto a aquisição dos dados, além  disso mede o tempo necessário para tal"
    t1_acq = time.perf_counter()
    scope.write('acquire:state 0')  # stop
    scope.write('acquire:stopafter SEQUENCE')  # single
    scope.write('acquire:state 1')  # run
    r = scope.query('*opc?')  # sync
    t2_acq = time.perf_counter()
    t_acq = t2_acq - t1_acq


    "Captura dos dados, além  disso mede o tempo necessário para tal"
    t1_data = time.perf_counter()
    # Dados obtidos do MDO, em formatação binária, além de estarem normalizados
    bin_normalized_wave = scope.query_binary_values('curve?', datatype='b', container=np.array)
    t2_data = time.perf_counter()
    t_data = t2_data - t1_data


    "Recupera os fatores de escala"
    # Escala de tempo
    tscale = float(scope.query('wfmoutpre:xincr?'))
    # Tempo Inicial
    tstart = float(scope.query('wfmoutpre:xzero?'))
    # Escala de tensão
    vscale = float(scope.query('wfmoutpre:ymult?'))  # volts / level
    # Offset
    voff = float(scope.query('wfmoutpre:yzero?'))  # reference voltage
    # Posição de referencia
    vpos = float(scope.query('wfmoutpre:yoff?'))  # reference position (level)


    'Verifica se houveram erros, caso sim, mostra quais flags foram levantadas'
    r = int(scope.query('*esr?'))
    print('event status register: 0b{:08b}'.format(r))
    r = scope.query('allev?').strip()
    print('all event messages: {}\n'.format(r))


    "Fecha a aquisição de dados"
    scope.close()
    rm.close()

    "Converte os dados obtidos(normalizados) em dados não normalizados"
    # horizontal (time)
    total_time = tscale * record_length
    tstop = tstart + total_time
    # Vetor tempo
    t = np.linspace(tstart, tstop, num=record_length, endpoint=False)

    # vertical (voltage)
    # Onda já em decimal normalizada
    normalized_wave = np.array(bin_normalized_wave, dtype='double')  # data type conversion
    # Onda decimal sem a normalização
    unnormalized_wave = (normalized_wave - vpos) * vscale + voff

    print("Finalizado processo de leitura")
    print("###################################################################\n")

    if reset is True:
        return unnormalized_wave, normalized_wave, bin_normalized_wave, t_reset, t_print_tela, t_acq, t_autoset, t_data
    else:
        return unnormalized_wave, normalized_wave, bin_normalized_wave, t_print_tela, t_acq, t_autoset, t_data

