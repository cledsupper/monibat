# Utilizado pelos módulos:
# -> events

from os import environ
from os.path import join, getmtime
import json
import time

from .constants import DEFAULT_SETTINGS

# $HOME/.config/Notify-Py
# PRESTE A ATENÇÃO A ALTERAR O NOME DESTE DIRETÓRIO
DIR = join(environ['HOME'], '.config', 'Notify-Py')
# $HOME/.config/Notify-Py/app.conf
# ESTA B****A DEPENDE DA VARIÁVEL ANTERIOR!!!
APP = join(DIR, 'config.json')

class Configuration():
    def __init__(self):
        self.data = DEFAULT_SETTINGS
        self._updated_at = 0
        self.update()

    def update(self):
        try:
            mt = getmtime(self.data)
            if mt <= self._updated_at:
                return
            with open(self.data) as file:
                self.data = json.load(file.read())
                self._updated_at = mt
        except FileNotFoundError:
            pass