# MonitBat para Termux

## Indicador de bateria altamente configurável com simulador de circuito de proteção.

<div align="center">
    <img src="https://github.com/cledsupper/monibat/blob/0b2519c4cd7051167c268b56957a506d7e3a4659/samples/preview.jpg" alt="MoniBat na barra de notificações do Android, mostrando tempo restante, percentual, temperatura, tensão e um score da saúde da bateria." style="height: 512px; width:236px;"/>
</div>

### INSTALAÇÃO

Instale as dependências necessárias:

1. Baixe via F-Droid e instale: Termux, Termux:Boot e Termux:API (versão 0.49 para o ícone do MoniBat funcionar);
2. Atualize o sistema com o comando (pkg upgrade);
3. Instale os pacotes "termux-api", "python" e, opcionalmente, "android-tools"¹.

Instale o MoniBat a partir do install.sh:

No diretório do MoniBat, execute:
> $ ./install.sh


### CONFIGURAÇÃO E CALIBRAÇÃO DA BATERIA ATRAVÉS DO EMULADOR DO MONIBAT

Inicialização automática:

Execute o Termux:Boot uma vez para que o MoniBat seja executado toda vez que reiniciar o sistema Android.

Calibre a bateria:

a) Modo manual, sem depuração por ADB:

1. Carregue completamente a bateria do seu celular. Quando chegar em 100%, observe a tensão através de um aplicativo auxiliar (sugestões: AccuBattery, BatteryBot Battery Indicator) etc.

2. No arquivo de configuração em .config/MoniBat, defina o percentual de carga fraca de acordo com as especificações da sua bateria -- você pode verificar essas informações através das bases de dados oriundas dos testes de (des)carga que vários cientistas fazem com baterias de lítio.

    2.1. Se a tensão estiver entre 4,35 e 4,4 V, defina o percentual de carga baixo como 15 %:

    ```json
    "percent": {
    ...
       "low": 15,
    ...
    ```

    2.2. Se a tensão estiver entre 4,25 e 4,34 V, defina o percentual de carga baixo como 20 %:

    ```json
    "percent": {
    ...
       "low": 20,
    ...
    ```

    2.3. Se o seu dispositivo Android é velho, possuindo uma bateria de lítio do início da década de 2010, é provável que a tensão máxima seja de 4,2 V, então, neste caso:

    ```json
    "percent": {
    ...
       "low": 30,
    ...
    ```

3. Também defina a capacidade da bateria para a capacidade "design" (ou de fábrica). Se a capacidade design é 5.000 mAh, divida-a por 1.000 (mil) para obter o valor em Ah, então escreva o número com um ponto em vez de vírgula (a parte fracionária é necessária mesmo que o número seja inteiro!):

    ```json
    "capacity": 0.0,
    "capacity_design": 5.0,
    ```

```
NOTE:

Nesse tipo de configuração, foi DISPENSÁVEL definir o parâmetro percent.fix. Esse parâmetro só deve ser usado em conjunto com percent.min e percent.max, caso o seu dispositivo não "calibre" a bateria ao entrar em sono profundo, ou durante a recarga. É o método mais fácil para corrigir o problema, que dispensa um contador de carga de bateria (o emulador do MoniBat).
```

4. Reinicie o MoniBat através do botão "reiniciar" quando a tensão mostrada pelo app auxiliar estiver em exatos 3,7 V ou um pouco menos que isso (no mínimo 3,68 V).

5. Carregue completamente o dispositivo, até aparecer o aviso de carga completa no Android. A capacidade máxima será salva quando o carregamento parar. Não use o dispositivo durante o carregamento!

```
NOTE:

Pode ser necessário reconectar o seu carregador se a bateria parou de carregar antes do Android mostrar 100 %, pois o sistema não "detectou" que a bateria está cheia.
```

6. Compare a capacidade salva no arquivo de configuração (ex.: 3.3 = 3300 mAh) com a capacidade "design" multiplicada pelo percentual de carga baixo (ex.: 5000 * 25% = 1250 mAh), então use a seguinte fórmula para calcular a capacidade real (y):
  y = (cf - ci)/ipb

```
NOTE:

 * cf: capacidade salva;
 * ci: capacidade vezes o percentual de carga baixo;
 * ipb: p inverso do percentual de carga baixo (100-p)/100
```

No exemplo acima, seria:

    y = (3300 - 1250)/[(100-25)/100]
    y = 2050/0,75 = 2733,33 mAh

Portanto, defina a capacidade real, em Ah, no arquivo de configuração:

```json
"capacity": 2.73333,
```

7. Reinicie o MoniBat mais uma vez antes de desconectar o carregador.


b) Modo automático com ADB:

1. Conecte o próprio ADB através da depuração por WiFi com a opção para pareamento por código:
  > $ adb pair IP:PORT # digite o código que aparece na tela do menu Desenvolvedor

```
NOTE:

É necessário dividir a tela ou usar o Termux em uma janela flutuante para conseguir fazer isso, já que o código de pareamento desaparece ao mudar de atividade.
```

2. Inicie o MoniBat (~/.termux/boot/moni.sh) e reinicie através da notificação para o programa executar como serviço.

3. Carregue completamente e depois use o dispositivo até que apareça a notificação de "calibração iniciada".

```
NOTE:

Após isso, você pode desativar a depuração via WiFi no menu desenvolvedor caso deseje economizar recursos.
```

4. Carregue o dispositivo Android completamente. Aqui é importante evitar o uso do aparelho, pois grandes e rápidas variações da corrente durante a recarga vão aumentar a imprecisão do emulador, assim comprometendo o resultado.

5. Após aparecer a notificação de calibração concluída, você pode reiniciar o MoniBat e matar o processo do ADB após um minuto do reinício do MoniBat (o tempo de tentativa do pareamento via WiFi).

```
NOTE:

Como na calibração manual, pode ser necessário reconectar o carregador caso a bateria tenha terminado a carga antes do sistema Android mostrar 100 %.
```

6. Desconecte do carregador e aproveite um celular que não descarga sem você saber!
