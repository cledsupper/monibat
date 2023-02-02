# tweaker.py - MoniBat Application Context and Configuration Class
#
#  Copyright (c) 2022, 2023 Cledson Ferreira
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
# -> events, service

import json
import logging
from typing import Optional

from batteryemulator import BatteryEmulator
from config.constants import *
from data.messages import *


def percent_abs(p: int) -> int:
    if p > 100:
        return 100
    elif p < 0:
        return 0
    return p


class Configuration():
    def __init__(self, toast_cb=None):
        self.data = DEFAULT_SETTINGS

        self.btweaks = {}
        self.delay = DELAY_CHARGING
        self.batt: BatteryEmulator = None
        self.o_tnow = None
        self.tnow = None
        self.btweaks = None
        self.o_btweaks = None
        self.chg_perc = None
        self.chg_time = None

        self.calibrated = CALIBRATION_STATE_NONE
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
                return False
            with open(FCONFIG, 'r') as file:
                data = json.load(file)
                errcode = self.valid_settings(data)
                self._updated_at = mt
        except FileNotFoundError:
            return False
        except:
            errcode = -1

        if self._sender:
            if errcode == 0:
                self._sender(TWEAKER_CFG_READ_SUCCESS)
            else:
                self._sender(TWEAKER_CFG_READ_FAILED % (errcode))
        return errcode > -1

    def save(self):
        err = None
        try:
            with open(FCONFIG, 'w') as file:
                file.write(json.dumps(self.data, indent=INDENTATION_DEFAULT))
        except Exception as e:
            err = e
        if err:
            logging.exception('Configuration.save()')
            self._sender(TWEAKER_CFG_SAVE_FAILED)
        else:
            self._updated_at = os.path.getmtime(FCONFIG)

    def valid_settings(self, settings) -> int:
        """Válida os parâmetros lidos antes de aplicar as configurações"""
        errcode = 0
        try:
            capacity = settings.get('capacity', None)
            if capacity is not None:
                assert isinstance(capacity, float)
            if not capacity:
                self.calibrated = CALIBRATION_STATE_NONE
            else:
                self.calibrated = CALIBRATION_STATE_FINAL

            design = settings.get(
                'capacity_design',
                DEFAULT_SETTINGS['capacity_design']
            )
            assert isinstance(design, float)

            self.data['capacity'] = capacity if capacity else design
            self.data['capacity_design'] = design
            if self.batt:
                self.batt._capacity_design = design
                self.batt._td_zero = 10*design if design else 20.0
                p = self.batt.percent - 1
                if capacity:
                    self.batt.start_emulating_cap(
                        capacity,
                        perc_start=p
                    )
                else:
                    self.batt.stop_emulating_cap()
        except AssertionError:
            errcode = 1

        infer = settings.get("infer_percent_always", False)
        self.data['infer_percent_always'] = bool(infer)

        adb_reflect = settings.get("adb_reflect", False)
        if self.data['adb_reflect'] != adb_reflect and not adb_reflect:
                self.batt.adb_dumpsys_reset()
        self.data['adb_reflect'] = bool(adb_reflect)

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
            errcode += 2

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

            typ = voltage.get('typ', VOLTAGE_TYP)
            assert typ > empty
            assert typ < full

            self.data['voltage'] = {
                'empty': empty,
                'full': full,
                'low': low,
                'high': high,
                'typ': typ
            }
        except AssertionError:
            errcode += 4

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
            errcode += 8

        return errcode

    def _percent_by_voltage(self, btweaks: dict) -> Optional[int]:
        v = btweaks["voltage"]
        if not v:
            return None

        status = btweaks["status"]
        vtyp = str(self.data["voltage"]["typ"])
        low = LEVEL_LOW_BY_VOLTAGE_TYP[vtyp]
        vmax = self.data["voltage"]["full"]
        vmin = self.data["voltage"]["empty"]
        vhigh = self.data["voltage"]["high"]
        vlow = self.data["voltage"]["low"]
        if status == 'Discharging':
            if v >= vlow:
                p = (v - vlow)/(vhigh - vlow)
                p = (100-low)*p + low
            else:
                p = (v - vmin)/(vlow - vmin)
                p = low*p
        else:
            p = 100*(v - vlow)/(vmax - vlow)
        return int(p)

    def percent_by_voltage(self, btweaks: dict) -> Optional[int]:
        v = btweaks["voltage"]
        if not v:
            return None

        vmax = self.data["voltage"]["full"]
        vmin = self.data["voltage"]["empty"]
        p = (v - vmin)/(vmax - vmin)
        p = 100*p
        return int(p)

    def fix_percent(self, btweaks: dict) -> int:
        """Corrige o percentual da bateria pela tensão ou por limites de menor e maior percentual de carga."""
        if self.data.get('infer_percent_always', False):
            p = self._percent_by_voltage(btweaks)
            if p:
                return percent_abs(p)

        p = btweaks['percent']

        if self.data['percent']['fix']:
            lmin = self.data['percent']['empty']
            lmax = self.data['percent']['full']
            p = (p-lmin)/(lmax-lmin)
            p = int(p*100)

        return percent_abs(p)

    def fix_status(self, btweaks: dict) -> str:
        """Corrige o status da bateria segundo a corrente de (des)carga em certas condições."""
        if self.batt._td_up is not None:
            zero = self.batt.zero
            if btweaks['status'] == 'Full':
                if btweaks['current'] >= zero:
                    return 'Charging'
            elif abs(btweaks['current']) < zero:
                return 'Not charging'
        return btweaks['status']

    def fix_health(self, btweaks: dict) -> str:
        """Corrige a saúde da bateria através da comparação entre a capacidade estimada e a capacidade real."""
        return btweaks['health']

    def infer_percent(self) -> int:
        """Infere o percentual da bateria em várias condições pressupostas."""
        status = self.batt.status
        v = self.batt.voltage
        if status == 'Full':
            return 100
        elif v:
            btweaks = {
                "status": status,
                "voltage": v
            }
            return percent_abs(self._percent_by_voltage(btweaks))
        vtyp = str(self.data["voltage"]["typ"])
        low = LEVEL_LOW_BY_VOLTAGE_TYP[vtyp]
        self.calibrated = CALIBRATION_STATE_MANUAL
        self.calibrate_aux = (low * self.data["capacity"]) / 100
        return low

    def reset_alarms(self):
        self.a_percent_high = False
        self.a_percent_low = False
        self.a_voltage_high = False
        self.a_voltage_low = False
        self.a_temp_hot = False
        self.a_temp_min = False
        self.a_temp_max = False
