# MonitBat para Termux

## Indicador de bateria altamente configurável com simulador de circuito de proteção.

<div align="center">
    <img src="https://github.com/cledsupper/monibat/raw/0b2519c4cd7051167c268b56957a506d7e3a4659/samples/preview.jpg" alt="MoniBat na barra de notificações do Android, mostrando tempo restante, percentual, temperatura, tensão e um score da saúde da bateria." style="height: 512px; width:236px;"/>
</div>

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

Calibre a bateria com ADB:

Infelizmente, para evitar erros de calibração, o emulador do MoniBat não tentará calibrar sem ter acesso à tensão da bateria. Portanto, será necessário o uso do ADB.

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


[]: [termux-platform-tools](https://github.com/rendiix/termux-adb-fastboot)
