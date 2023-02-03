# batterydriver.py - MoniBat Termux:API Battery Interface
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
# -> events

import json
import logging
import shlex
import subprocess
from typing import Dict, Any

from config.constants import ADB_STATUS, BATTERY_COMMAND, DRIVER_SLEEP, DRIVER_CURRENT_MAX, SUBPROCESS_TIMEOUT
from batteryemulator import time, BatteryEmulator, Optional


def to_linux_str(termux_str: str) -> str:
    return termux_str[0] + termux_str[1:].lower().replace('_', ' ')


class Battery(BatteryEmulator):
    """Classe Battery para acessar informações da bateria"""

    # NOTE: rendiix has an ADB fork for Galaxy devices which actually works
    HAS_ADB = False

    def __init__(self, command: str = BATTERY_COMMAND, cap: Optional[float] = None):
        """
        Construtor do driver.

        ### Parâmetros opcionais:
        - command [str]: comando Termux:API para obter estado da bateria.
        - cap [float | None]: capacidade em Ampère-hora (Ah).
        """
        super().__init__(cap=cap)
        try:
            subprocess.run(
                shlex.split('adb wait-for-device'),
                check=True,
                timeout=SUBPROCESS_TIMEOUT
            )
            Battery.HAS_ADB = True
        except:
            pass

        self._cmd = command

        self._sp_data: Dict[str, Any] = {}
        """Dados retornados pela Termux:API"""

        self._sp_last_call = 0
        """Tempo UNIX da última chamada à Termux:API"""

        # Default and non-refreshable values
        self._unit = 'A'
        self._technology = 'Li-ion'
        self._status = 'Unknown'
        self._pstatus = self._status
        self._mocking = False

        self.refresh()
        # check for valid current values
        c = self._sp_data['current']
        if abs(c) > DRIVER_CURRENT_MAX:
            self._csign = 1000.0
        else:
            self._csign = 1.0
        c /= self._csign
        if abs(c) <= DRIVER_CURRENT_MAX:
            self._td_up = False
            # check for inverse charging polarity
            if (not self._charging and c > self._td_zero)\
                    or (self._charging and c < -self._td_zero):
                self._csign *= -1.0
                c *= -1.0
            self._current_now = c / 1000
            self._current_now_milis = c
        else:
            self._current_now = None
            self._current_now_milis = None

    def refresh(self):
        """Pula múltiplas chamadas à Termux:API até um tempo específico: DRIVER_SLEEP."""
        tnow = time.time()
        td = tnow - self._sp_last_call
        if td < DRIVER_SLEEP:
            return
        self._sp_last_call = tnow

        self._voltage = self.adb_voltage()
        if self._td_up and Battery.HAS_ADB:
            self._td_refresh_percent()
            try:
                self._charging = self.adb_status() == 'Charging'
                self._temp = self.adb_temp()
                self._health = self.adb_health()
                self._status = self.adb_status()
                self._td_refresh_current(self.adb_current()*1000, self._status)
                return
            except:
                self.adb_dumpsys_reset()

        while True:
            try:
                proc = subprocess.run(
                    shlex.split(self._cmd),
                    capture_output=True,
                    check=True,
                    timeout=SUBPROCESS_TIMEOUT
                )
                break
            except subprocess.SubprocessError as e:
                logging.debug(e)
                logging.debug(
                    " :::===::: CHILD PROCESS' ERROR OUTPUT :::===:::")
                logging.debug(e.stderr.decode() if e.stderr else '')
                logging.debug(
                    " :===: END OF CHILD PROCESS' ERROR OUTPUT :===:")

        text = proc.stdout
        self._sp_data = json.loads(text)
        if not self._td_up:
            self._percent = self._sp_data['percentage']
            self._energy_now = None
        else:
            self._td_refresh_percent()

        self._charging = self._sp_data['status'] == 'CHARGING'
        self._temp = self._sp_data['temperature']
        self._health = to_linux_str(self._sp_data['health'])
        self._status = to_linux_str(self._sp_data['status'])

        if self._td_up is not None:
            self._td_refresh_current(self._sp_data['current'], self._status)

    def driver_stop(self):
        if Battery.HAS_ADB:
            self.adb_dumpsys_reset()

    def adb_read(self, filename) -> Optional[str]:
        value = None
        try:
            proc = subprocess.run(
                shlex.split(
                    'adb shell cat /sys/class/power_supply/battery/%s' % (filename)
                ),
                capture_output=True,
                check=True,
                timeout=1
            )
            value = proc.stdout.decode().strip()
        except:
            pass
        return value

    def adb_voltage(self):
        """Tensão da bateria (V)."""
        if not Battery.HAS_ADB:
            return None
        value = self.adb_read('voltage_avg')
        if value is None:
            value = self.adb_read('voltage_now')
        if value is None:
            return None
        return float(value) / 1000000

    def adb_status(self):
        return self.adb_read('status')

    def adb_health(self):
        return self.adb_read('health')

    def adb_temp(self):
        value = self.adb_read('temp')
        return float(value) / 10

    def adb_current(self):
        value = self.adb_read('current_avg')
        if value is None:
            self.adb_read('current_now')
        # values are reported on mA when device is Galaxy A20
        return float(value) / 1000

    def _td_refresh_percent(self):
        self._percent = 1 + 100*(self._td_eng / self._td_cap)
        self._percent = int(self._percent)
        self._energy_now = self._td_eng / 1000

    def _td_refresh_current(self, current: float, status: str):
        c = current
        c /= self._csign
        # the Galaxy A20 take a long time to refresh current when unplugged
        if status == 'Discharging' and c > self._td_zero:
            c *= -1.0
        self._current_now = c / 1000
        self._current_now_milis = c

    def adb_dumpsys_reset(self):
        if self._mocking:
            subprocess.run(
                shlex.split(
                    'adb shell dumpsys battery reset'
                ),
                timeout=1
            )
            self._mocking = False

    def _adb_dumpsys_set(self, param: str, value: str):
        subprocess.run(
            shlex.split(
                'adb shell dumpsys battery set %s %s' % (param, value)
            ),
            check=True,
            capture_output=True,
            timeout=1
        )

    def adb_reflect(self):
        if not (self._td_up and Battery.HAS_ADB):
            return
        if self._status != self._pstatus:
            self.adb_dumpsys_reset()
            self._pstatus = self._status
            self._mocking = True

        self._adb_dumpsys_set('level', str(self._percent))
        self._adb_dumpsys_set('status', str(ADB_STATUS[self._status]))
        scale = int(100 * self._capacity / self._capacity_design)
        self._adb_dumpsys_set('scale', str(scale))
        if self._td_eng:
            self._adb_dumpsys_set('counter', str(int(self._td_eng*1000)))
        self._adb_dumpsys_set('temp', str(int(self._temp*10)))


if __name__ == '__main__':
    battery = Battery()
    print("Starting emulator...")
    battery.start_emulating_cap(2.0, 50)
    print(battery.percent)
    print(battery.current_now)
    print(battery.voltage)
    battery.stop_emulating_cap()
