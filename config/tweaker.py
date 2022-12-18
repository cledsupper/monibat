# Utilizado pelos módulos:

from os import environ
from os.path import join

# $HOME/.config/leshto-batt
# PRESTE A ATENÇÃO A ALTERAR O NOME DESTE DIRETÓRIO
DIR = join(environ['HOME'], '.config', 'leshto-batt')
# $HOME/.config/leshto-batt/app.conf
# ESTA B****A DEPENDE DA VARIÁVEL ANTERIOR!!!
APP = join(DIR, 'app.conf')
