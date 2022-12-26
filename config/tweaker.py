# tweaker.py - MoniBat Application Context and Configuration Class
#
#  Copyright (c) 2022 Cledson Ferreira
#
#  Author: Cledson Ferreira <cledsonitgames@gmail.com>
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation; either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
#  USA

# Utilizado pelos módulos:
# -> eventloop, events

import json
import logging
from typing import Optional

from .constants import *


class Configuration():
    def __init__(self, toast_cb=None):
        self.data = DEFAULT_SETTINGS
        self.btweaks = {}
        self.delay = DELAY_CHARGING
        self.batt = None
        self.o_tnow = None
        self.tnow = None
        self.btweaks = None
        self.o_btweaks = None
        self.calibrate = False
        self.calibrate_aux = 0.0

        self._updated_at = 0
        self._sender = None
        self.update()
        self.reset_alarms()
        self._sender = toast_cb

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

    def save(self):
        err = None
        try:
            with open(FCONFIG, 'w') as file:
                file.write(json.dumps(self.data))
        except Exception as e:
            err = e
        if err:
            logging.exception('Configuration.save()')
            self._sender('falha ao salvar configuração!')
        else:
            self._updated_at = os.path.getmtime(FCONFIG)

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

            low = voltage.get('low', VOLTAGE_LOW)
            high = voltage.get('high', VOLTAGE_FULL)
            assert low < high
            assert low > VOLTAGE_EMPTY

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
            p = (p-lmin)/(lmax-lmin)
            p = int(p*100)

        if p > 100:
            p = 100
        elif p < 0:
            p = 0

        return p

    def fix_status(self, btweaks: dict):
        capacity = self.data['capacity']
        if capacity:
            if btweaks['status'] == 'Full':
                if btweaks['current'] >= 0.01*capacity:
                    return 'Charging'
            elif abs(btweaks['current']) < 0.01*capacity:
                return 'Not charging'
        return btweaks['status']

    def infer_percent(self, driver):
        v = driver.voltage()
        if v:
            status = driver.status()
            if status == 'Discharging':
                vhigh = self.data["voltage"]["high"]
                vempty = self.data["voltage"]["empty"]
                p = (v - vempty)/(vhigh - vempty)
            else:
                vfull = self.data["voltage"]["full"]
                vlow = self.data["voltage"]["low"]
                p = (v - vlow)/(vfull - vlow)
            p = int(p*100)
            if p > 100:
                p = 100
            elif p < 0:
                p = 0
            return p
        return self.data["percent"]["low"]

    def reset_alarms(self):
        self.a_percent_high = False
        self.a_percent_low = False
        self.a_voltage_high = False
        self.a_voltage_low = False
        self.a_temp_hot = False
        self.a_temp_min = False
        self.a_temp_max = False
