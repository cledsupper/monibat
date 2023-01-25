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

from config.constants import BATTERY_COMMAND, DRIVER_SLEEP, DRIVER_CURRENT_MAX, SUBPROCESS_TIMEOUT
from batteryemulator import time, BatteryEmulator


def to_linux_str(termux_str: str) -> str:
    return termux_str[0] + termux_str[1:].lower().replace('_', ' ')


class Battery(BatteryEmulator):
    """Classe Battery para acessar informações da bateria"""

    # NOTE: rendiix has an ADB fork for Galaxy devices which actually works
    HAVE_ADB = False

    def __init__(self, command: str = BATTERY_COMMAND):
        super().__init__()
        try:
            subprocess.run(
                shlex.split('adb wait-for-device'),
                check=True,
                timeout=SUBPROCESS_TIMEOUT
            )
            Battery.HAVE_ADB = True
        except:
            pass
        self._cmd = command
        self._sp_data: Dict[str, Any] = {}
        self._sp_last_call = 0.0

        # Default and non-refreshable values
        self._unit = 'A'
        self._capacity_design = None
        self._technology = 'Li-ion'

        self.refresh()
        if abs(self._sp_data['current']) <= DRIVER_CURRENT_MAX:
            self._td_up = False
            c = self._sp_data['current']
            self._current_now = (c / 1000) if c is not None else None
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
                logging.exception(e)
                logging.error(
                    " :::===::: CHILD PROCESS' ERROR OUTPUT :::===:::")
                logging.error(e.stderr.decode() if e.stderr else '')
                logging.error(
                    " :===: END OF CHILD PROCESS' ERROR OUTPUT :===:")

        text = proc.stdout
        self._sp_data = json.loads(text)
        if self._td_up:
            self._percent = 1 + 100*(self._td_eng / self._td_cap)
            self._percent = int(self._percent)
            self._capacity = self._td_cap / 1000
            self._energy_now = self._td_eng / 1000
        else:
            self._percent = self._sp_data['percentage']
            self._capacity = None
            self._energy_now = None

        self._charging = self._sp_data['status'] == 'CHARGING'
        self._temp = self._sp_data['temperature']
        self._voltage = self.adb_voltage()
        self._health = to_linux_str(self._sp_data['health'])
        self._status = to_linux_str(self._sp_data['status'])

        if self._td_up is not None:
            c = self._sp_data['current']
            self._current_now = (c / 1000) if c is not None else None
            self._current_now_milis = c

    def adb_voltage(self):
        """Tensão da bateria (V)"""
        value = 0.0
        if Battery.HAVE_ADB:
            try:
                proc = subprocess.run(
                    shlex.split(
                        'adb shell cat /sys/class/power_supply/battery/voltage_avg'
                    ),
                    capture_output=True,
                    check=True,
                    timeout=1
                )
                value = float(int(proc.stdout.decode().strip()))
                value = value/1000000.0
            except:
                pass
        if value:
            return value
        return None


if __name__ == '__main__':
    battery = Battery()
    print("Starting emulator...")
    battery.start_emulating_cap(2.0, 50)
    print(battery.percent)
    print(battery.current_now)
    battery.stop_emulating_cap()
