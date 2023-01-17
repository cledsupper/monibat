# MonitBat para Termux

## Indicador de bateria altamente configurável com contador de carga.

<div align="center">
    <img src="https://github.com/cledsupper/monibat/raw/0b2519c4cd7051167c268b56957a506d7e3a4659/samples/preview.jpg" alt="MoniBat na barra de notificações do Android, mostrando tempo restante, percentual, temperatura, tensão e um score da saúde da bateria." style="height: 512px; width:236px;"/>
</div>

Note: este programa é um projeto conceitual para desenvolvedories interessades, o que significa que, no futuro, será construída uma versão amigável para utilizadories sem conhecimento em programação. No entanto, preciso de recur$os para conseguir tornar este projeto possível.

Se você utilizou ou/e quer que eu desenvolva um aplicativo muito mais simples para uso por seres humanos, leia a última seção do presente documento para detalhes de como apoiar.


### INSTALAÇÃO

Instale as dependências necessárias:

1. Baixe via F-Droid e instale: Termux, Termux:Boot e Termux:API (versão 0.49 para o ícone do MoniBat funcionar);
2. Atualize o sistema com o comando (pkg upgrade);
3. Instale os pacotes "termux-api", "python" e "android-tools" (ou a versão do ADB por rendiix[^1] que corrige erro em smartphones Galaxy).

Instale o MoniBat a partir do install.sh:

No diretório do MoniBat, execute:
> $ ./install.sh


### CONFIGURAÇÃO E CALIBRAÇÃO DA BATERIA ATRAVÉS DO EMULADOR DO MONIBAT

Inicialização automática:

Execute o Termux:Boot uma vez para que o MoniBat seja executado toda vez que reiniciar o sistema Android.

```
NOTE:

Desative a otimização de bateria (ou a opção "sem restrição" de execução em segundo plano) para o Termux, Termux:Boot e Termux:API!
Caso contrário o processo do MoniBat será encerrado pelo task killer do Android.
```

O processo de calibração foi idealizado apenas conforme a opção (b). No entanto, porque nem todes possuem o conhecimento necessário, ou não tem tempo livre para parear o ADB do próprio dispositivo com as ferramentas Android do Termux, estarei mantendo a forma de calibração do ítem (a).


#### a) Calibre a bateria apenas reiniciando o serviço:

1. Descubra e configure a tensão nominal da sua bateria a partir de uma carga completa.

    1. Se a tensão for maior que 4,34 V, é porque a bateria do seu smartphone/tablet é de 3,85 V de tensão típica. Defina isto no arquivo do configuração[^2]:

    ```json
    "voltage": {
        ...
        "typ": 3.85
    }
    ```

    2. Se a tensão for maior que 4,2 V, é porque a bateria é de 3,8 V de tensão típica. Defina isto no arquivo de configuração:
  
    ```json
    "voltage": {
        ...
        "typ": 3.8
    }
    ```


    3. No entanto, se a tensão for 4,2 V:
    ```json
    "voltage": {
        ...
        "typ": 3.7
    }
    ```

Pack de baterias em paralelo (tensões diferentes das especificadas acima) não é suportado por padrão! no entanto, é possível adicionar o suporte ao duplicar e modificar uma linha do arquivo constants.py, o dicionário LEVEL_LOW_BY_VOLTAGE_TYP. Após isso, basta modificar o arquivo de configuração[^2] para as voltagens serem multiplicadas em duas, três ou mais células.

2. Execute o MoniBat. Ele vai mostrar um nível de bateria muito baixo (15, 20 ou 30 %), mas é INCORRETO.

Para executar o MoniBat sem precisar reiniciar o sistema Android:
> ~/.termux/boot/moni.sh

Isso vai prender o seu terminal por pelo menos um minuto se o ADB estiver instalado no Termux. Após aparecer a notificação, você pode tocar no botão "recalibrar" para que a linha de comandos seja liberada. Pode demorar pouco mais de um minuto para recuperar a linha de comandos se o ADB estiver instalado, ou dez segundos caso contrário.


3. Descarregue o dispositivo até a tensão atingir 3,7 V (é um nível de energia fraco, mas ainda seguro). Você pode acompanhar a tensão com um aplicativo gratuito como o [BatteryBot Status Indicator](https://play.google.com/store/apps/details?id=com.darshancomputing.BatteryIndicator).


4. Neste ponto, reinicie o MoniBat pelo botão "recalibrar". Quando o nível de bateria mudar para o mesmo nível baixo de quando você o iniciou pela primeira vez, você deve carregar o dispositivo COMPLETAMENTE.

```
NOTE:

Pode ser necessário desconectar e conectar o carregador mais uma vez se não aparecer nenhuma notificação de calibração concluída, pois, neste caso, a bateria deve ter terminado de carregar antes mesmo do Android mostrar 100 %.
Quando aparecer a notificação de calibração concluída, neste momento você pode desconectar o carregador e deixar o MoniBat executando em segundo plano.
```


#### b) Calibre a bateria com ADB:

Será necessário parear o ADB no próprio dispositivo com o Termux e uma conexão WiFi estável (não tente calibrar com o ADB em redes públicas!).

1. Conecte o próprio ADB através da depuração por WiFi com a opção para pareamento por código:
  > $ adb pair IP:PORT # digite o código que aparece na tela do menu Desenvolvedor

```
NOTE:

É necessário dividir a tela ou usar o Termux em uma janela flutuante para conseguir fazer isso, já que o código de pareamento desaparece ao mudar de atividade.
```

Se o comando acima não conectar o ADB, desinstale o android-tools padrão e tente instalar esta versão[^1].


2. Inicie o MoniBat (~/.termux/boot/moni.sh) e reinicie através da notificação para o programa executar como serviço.

3. Carregue completamente e depois use o dispositivo até que apareça a notificação de "calibração iniciada".


```
NOTE:

Se o ADB desconectou, não se preocupe, pois basta religar o WiFi, reativar a depuração por WiFi nas configurações do aparelho, e executar o comando "adb kill-server" no Termux.
O MoniBat continuará tentando executando comandos ADB, o que fará ele ser reconectado automaticamente.
```


4. Carregue o dispositivo Android completamente. Aqui é importante evitar o uso do aparelho, pois grandes e rápidas variações da corrente durante a recarga vão aumentar a imprecisão do emulador, assim comprometendo o resultado.

```
NOTE:

Como na calibração manual, pode ser necessário reconectar o carregador caso a bateria tenha terminado a carga antes do sistema Android mostrar 100 %.
```

5. Agora é a etapa final, pois o processo de calibração não será definitivo com uma bateria velha.

Se a sua bateria for velha (mais de um ano), tendo uma taxa de autodescarga elevada, é necessário descarregar até 15 % mantendo o ADB conectado. Caso contrário, toque no botão reiniciar mesmo se a notificação de calibração solicitou que você a descarregue até 15 %.

6. Após aparecer a notificação de calibração concluída, religue o WiFi, reinicie o MoniBat e encerre o ADB com o comando "adb kill-server".


[^1]: [termux-platform-tools](https://github.com/rendiix/termux-adb-fastboot)

[^2]: O arquivo está localizado na pasta "samples" ou ainda, se o MoniBat já estiver instalado, "~/.config/MoniBat".
