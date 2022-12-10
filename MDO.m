function [sinais]=MDO(varargin)
% ==============================================================
% quando o MDO for utilizado na função de AFG o sinal xt deve ser
% normalizado.

% ================= REGIÃO EDITÁVEL ==================================
%% Conexão do Instrumento
 esp = varargin{1};      % recebe a especificação do sinal
 obj1 = varargin{2};
 deviceObj = varargin{3};
% % ================= REGIÃO NÃO-EDITÁVEL ===============================
% if esp.conexao=='lan';
%     visa_address=strcat('TCPIP::',esp.ip,'::INSTR');
%     obj1 = instrfind('Type', 'visa-tcpip', 'RsrcName', visa_address, 'Tag', '');
%     
% else
%     visa_address = esp.usb;
%     obj1 = instrfind('Type', 'visa-usb', 'RsrcName', visa_address, 'Tag', '');
% end
% 
% if isempty(obj1) ;% cria um visa
%     obj1 = visa('TEK', visa_address);
% else
%     fclose(obj1);
%     obj1 = obj1(1);
% end
% 
% set(obj1, 'InputBufferSize', 1048576);
% set(obj1, 'OutputBufferSize', 1048576);
% 

sinais.tr=0;sinais.xr=0;

%% ========================= TRANSMISSÃO =================================
if esp.funcao=='tx'
    fopen(obj1);
    dpo=obj1;
    
    mens=strcat('Transmitindo sinal',{' '},esp.FormaOnda,{' '},'para o AFG...\n');
    %clc;
    fprintf(mens{1});
    
    fwrite(dpo, '*CLS');                            % religa o afg?
    fwrite(dpo,'AFG:OUTPut:STATE ON');
    fwrite(dpo,'AFG:OUTPut:LOAd:IMPEDance HIGHZ');
    
    %% Sinal Arbitrário
    if esp.FormaOnda=='arb'
        fwrite(dpo, 'AFG:FUNC Arb');
        x=varargin{4};
        a=x.xt;
        t=x.tt;
        
        %% transforma double em ASCII
        apal=[];
        for i=1:length(a)
            apal=strcat(apal,num2str(a(i)),',');
        end
        
        
        tempo=strcat('AFG:PERIOD',{' '}, num2str(t(end)+t(2)-t(1)));
        fwrite(dpo,tempo{1});
        
        sinalconv=strcat('AFG:ARBitrary:EMEM:POINTS ',{' '},apal(1:end-1));
        fwrite(dpo,sinalconv{1});
        
        %% Altera escala para mais próxima se setado o scale automático
        if esp.scale_automatico==1 % caso o usuário queira o ajuste automático da escala
            tt=varargin{1};
%            a=query(dpo,'HORizontal:SCAle?');
%            fs_o = 1/(1*str2num(a)/10e3);
             fs_o =  tt.frequencia/1;
            Fs=[2.5 5 10 25 50 100 250 500 1e3 2.5e3 5e3 10e3 25e3 50e3 100e3 250e3 500e3 1e6 2.5e6 5e6 10e6 25e6 50e6 100e6 250e6 500e6 1.25e9 2.5e9];
            %
            for cont=1:length(Fs)
                if Fs(cont)>=fs_o, break;end
            end
            T_o = 1/(1*Fs(cont)/10e3);
            mess=strcat('HORizontal:SCAle ',{' '},num2str(T_o));
            fwrite(dpo,mess{1});
            %
        end
        
        %% Sinal Transcedental
    elseif esp.FormaOnda=='sin'
        fwrite(dpo, 'AFG:FUNC SINE');
    elseif esp.FormaOnda=='ram'
        fwrite(dpo, 'AFG:FUNC RAMP');
    elseif esp.FormaOnda=='squ'
        fwrite(dpo, 'AFG:FUNC SQUare');
    end
    offset=strcat('AFG:OFFSet',{' '},num2str(esp.offset));
    fwrite(dpo,offset{1});
    amplitude = strcat('AFG:AMPLitude',{' '},num2str(esp.amplitude));
    fwrite(dpo,amplitude{1});
    
    if isequal(esp.FormaOnda,'arb')==0
        frequencia = strcat('AFG:FREQuency',{' '},num2str(esp.frequencia));
%         fwrite(dpo,['AFG:FREQuency ' num2str]);
        fwrite(dpo,frequencia{1});
    end
    
    if esp.autoset==1
        fwrite(dpo,'AUTOSET EXECUTE');
    end
    %     escala = 1/(10*/10e3);
    %     fwrite(dpo,'CH4:SCALE 500E-03')
    if esp.alinhar==1
        fwrite(dpo,'CH1:POSition 0');
        fwrite(dpo,'CH2:POSition 0');
    end
    
    %% ========================== RECEPÇÃO =================================
elseif esp.funcao=='rx'
    
    
    %%
%     % recebe o sinal
%     deviceObj = icdevice('DPO4034.mdd', obj1); %here the buffer gets small again
%     
%     % Connect device object to hardware.
     connect(deviceObj);
    
    
    %clc;
    fprintf('Recebendo sinal do Osciloscópio...\n');
    
    
    % Execute device object function(s).
    groupObj = get(deviceObj, 'Waveform');
    groupObj = groupObj(1);
    
    if esp.canais(1)==1
        if esp.Z(1)==0
            fwrite(obj1,'CH1:TERmination MEG'); %added this option for VLC2
        else
            fwrite(obj1,'CH1:TERmination FIFty');
        end
        if esp.COUP(1)== 0
            fwrite(obj1,'CH1:COUP AC');
        elseif esp.COUP(1)== 1
            fwrite(obj1,'CH1:COUP DC');
        end
        [sinais.xr1,tr1] = invoke(groupObj, 'readwaveform', 'channel1');  %obtém a forma de onda mostrada no canal 1
        sinais.tr1=-min(tr1)+tr1;
    end
    if esp.canais(2)==1
        if esp.Z(2)==0
            fwrite(obj1,'CH2:TERmination MEG');
        else
            fwrite(obj1,'CH2:TERmination FIFty');
        end
        if esp.COUP(2)== 0
            fwrite(obj1,'CH2:COUP AC');
        elseif esp.COUP(2)== 1
            fwrite(obj1,'CH2:COUP DC');
        end
        [sinais.xr2,tr2]= invoke(groupObj, 'readwaveform', 'channel2'); %obtém a forma de onda mostrada no canal 2
        sinais.tr2=-min(tr2)+tr2;
    end
    
    %     plot(x,y)
    % Funções úteis
    %     freq=query(dpo,'AFG:Frequency?')
    %     func=query(dpo, 'AFG:FUNC?')
    % fwrite(dpo, 'AFG:FUNC Noise');
    %     fwrite(dpo, 'AFG:FUNC Squar');
    %     freq=strcat('AFG:Frequency',{' '}, '3*1e6');
    %     fwrite(dpo,freq{1})
    
end
disconnect(deviceObj);
fclose(obj1);
% clc; fprintf('Aquisição realizada com sucesso!...\n');


%% Outros
%
% [/ACQ:STATE OFF;
% ACQ:MOD SAM;
% ACQ:STOPA SEQ;
% SEL:CH1 ON;
% CH1:COUP DC;
% CH1:OFFS 0.0;
% CH1:SCA 1.0;
% CH1:IMP MEG;
% CH1:BAN FUL;
% CH1:LAB "15ms pulse";
% SEL:CH2 ON;
% CH2:COUP DC;
% CH2:POS -3;
% CH2:OFFS 0.0;
% CH2:SCA 5.0;
% CH2:IMP MEG;
% CH2:BAN FUL;
% CH2:LAB "Turn On-Turn Off";
% HOR:MAI:SCA 200E-6;
% HOR:MAI:POS 0.1;
% HOR:DEL:MOD ON;
% HOR:DEL:TIM 400E-6;
% TRIG:A:TYP EDG;
% TRIG:A:EDGE:SOU CH1;
% TRIG:A:LEV 0.1;
% TRIG:A:EDGE:SLO RIS;
% TRIG:A:EDGE:COUP DC;
% DIS:INTENSIT:WAVEFORM 75;
% ACQ:STATE ON
%
% AFG:OUTPUT:LOAD:IMPEDANCE HIGHZ;
% AFG:FUNCTION PULSE;
% AFG:LOWLEVEL 0.0;
% AFG:HIGHLEVEL 1.8;
% AFG:PERIOD 64.8E-3;
% AFG:PULSE:WIDTH 16.2E-3

% Limpa registradores
%     fwrite(dpo, '*RST'); % desliga o afg?
%     fwrite(dpo, '*CLS'); % religa o afg?

