# Utilizado pelos módulos:
# -> eventloop, events

import json
import time

from .constants import *

class Configuration():
    def __init__(self, toast_cb = None):
        self.data = DEFAULT_SETTINGS
        self.charge = None
        self.xch = XCH_AWAKE # convert mA(6 secs) to mAh
        self._updated_at = 0
        self._sender = toast_cb
        self.update()

    def update(self):
      errcode = 0
      try:
        mt = os.path.getmtime(FCONFIG)
        if mt <= self._updated_at:
          return
        with open(FCONFIG, 'r') as file:
          data = json.load(file)
          errcode = self.valid_settings(data)
          self._updated_at = mt
      except FileNotFoundError:
        return
  
      if self._sender:
        if errcode == 0:
          self._sender('configuração atualizada')
        else:
          self._sender('erro de config., cód.: %d' % (errcode))

    def valid_settings(self, settings):
        """Válida os parâmetros lidos antes de aplicar as configurações"""
        errcode = 0
        try:
          capacity = settings.get('capacity', DEFAULT_SETTINGS['capacity'])
          assert isinstance(capacity, float)
          self.data['capacity'] = capacity
        except AssertionError:
          errcode = 1
  
        try:
          percent = settings.get('percent', DEFAULT_SETTINGS['percent'])
          assert isinstance(percent, dict)
          empty = percent.get('empty', LEVEL_EMPTY)
          full = percent.get('full', LEVEL_FULL)
          assert empty < full
          assert empty >= LEVEL_EMPTY
          assert full <= LEVEL_FULL

          fix = percent.get('fix', False)
          assert isinstance(fix, bool)

          low = percent.get('low', LEVEL_EMPTY+1)
          high = percent.get('high', LEVEL_FULL-1)
          assert low < high
          assert low > LEVEL_EMPTY
          assert high < LEVEL_FULL
          
          self.data['percent'] = {
            'empty': empty,
            'full': full,
            'fix': fix,
            'low': low,
            'high': high
          }
        except AssertionError:
          errcode = 2

        try:
          voltage = settings.get('voltage', DEFAULT_SETTINGS['voltage'])
          assert isinstance(voltage, dict)
          empty = voltage.get('empty', VOLTAGE_EMPTY)
          full = voltage.get('full', VOLTAGE_FULL)
          assert empty < full

          low = voltage.get('low', VOLTAGE_EMPTY+0.2)
          high = voltage.get('high', VOLTAGE_FULL-0.1)
          assert low < high
          assert low > VOLTAGE_EMPTY
          assert high < VOLTAGE_FULL

          self.data['voltage'] = {
            'empty': empty,
            'full': full,
            'low': low,
            'high': high
          }
        except AssertionError:
          errcode = 3

        try:
          temp = settings.get('temp', DEFAULT_SETTINGS['temp'])
          assert isinstance(temp, dict)
          min = temp.get('min', TEMP_MIN)
          hot = temp.get('hot', TEMP_HOT)
          max = temp.get('max', TEMP_MAX)
          assert min >= TEMP_MIN
          assert hot > min
          assert hot < max
          assert max <= TEMP_MAX

          self.data['temp'] = {
            'min': min,
            'hot': hot,
            'max': max
          }
        except AssertionError:
          errcode = 4
        
        return errcode

    def fix_percent(self, btweaks: dict):
      p = btweaks['percent']

      if self.data['percent']['fix']:
        lmin = self.data['percent']['empty']
        lmax = self.data['percent']['full']
        if lmin or lmax != 100:
          p = (p-lmin)/(lmax-lmin)
          p = int(p*100)
        elif self.charge is not None:
          p = self.charge / self.data['capacity']
          p = int(p*100)
        if p < 0:
          p = 0
        elif p > 100:
          p = 100
  
      return p

    def fix_status(self, btweaks: dict):
      capacity = self.data['capacity']
      if capacity:
        if abs(btweaks['current']) < 0.01*capacity:
          return 'Not charging'
      return btweaks['status']