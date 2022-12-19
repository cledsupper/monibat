# Utilizado pelos módulos:
# -> events

from os import environ
from os.path import join, getmtime
import json
import time

from .constants import DEFAULT_SETTINGS, MAX_LEVEL_FULL, MIN_LEVEL_EMPTY, VOLTAGE_EMPTY, VOLTAGE_FULL, TEMP_HOT, TEMP_MAX, TEMP_MIN

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
                data = json.load(file.read())
                self.valid_settings(data)
                self._updated_at = mt
        except FileNotFoundError:
            pass

    def valid_settings(self, settings):
        """Válida os parâmetros lidos antes de aplicar as configurações"""
        percent = settings.get('percent', DEFAULT_SETTINGS['percent'])
        empty = percent.get('empty', MIN_LEVEL_EMPTY)
        full = percent.get('full', MAX_LEVEL_FULL)
        assert empty < full
        assert empty >= MIN_LEVEL_EMPTY
        assert full <= MAX_LEVEL_FULL

        fix = percent.get('fix', False)
        assert isinstance(fix, bool)

        low = percent.get('low', MIN_LEVEL_EMPTY+1)
        high = percent.get('high', MAX_LEVEL_FULL-1)
        assert low < high
        assert low >= MIN_LEVEL_EMPTY
        assert high <= MAX_LEVEL_FULL

        percent = {
            'empty': empty,
            'full': full,
            'fix': fix,
            'low': low,
            'high': high
        }

        voltage = settings.get('voltage', DEFAULT_SETTINGS['voltage'])
        empty = voltage.get('empty', VOLTAGE_EMPTY)
        full = voltage.get('full', VOLTAGE_FULL)
        assert empty < full

        low = voltage.get('low', VOLTAGE_EMPTY+0.2)
        high = voltage.get('high', VOLTAGE_FULL-0.1)
        assert low < high
        assert low > VOLTAGE_EMPTY
        assert high < VOLTAGE_FULL

        voltage = {
            'empty': empty,
            'full': full,
            'low': low,
            'high': high
        }

        temp = settings.get('temp', DEFAULT_SETTINGS['temp'])
        min = temp.get('min', TEMP_MIN)
        hot = temp.get('hot', TEMP_HOT)
        max = temp.get('max', TEMP_MAX)
        assert min >= TEMP_MIN
        assert hot > min
        assert hot < max
        assert max <= TEMP_MAX

        temp = {
            'min': min,
            'hot': hot,
            'max': max
        }

        self.data = {
            'percent': percent,
            'voltage': voltage,
            'temp': temp
        }