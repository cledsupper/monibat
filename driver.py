# driver.py - MoniBat Termux:API Battery Interface and Capacity Counter
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
import time
import threading
from typing import Dict, Any

from config.constants import BATTERY_COMMAND, DRIVER_SLEEP, DRIVER_CURRENT_MAX, LEVEL_LOW, SUBPROCESS_TIMEOUT
from batteryinterface import BatteryInterface


def to_linux_str(termux_str: str) -> str:
    return termux_str[0] + termux_str[1:].lower().replace('_', ' ')


class Battery(BatteryInterface):
    """Classe Battery para acessar informações da bateria"""

    # NOTE: rendiix has an ADB fork for Galaxy devices which actually works
    HAVE_ADB = False

    def __init__(self, command: str = BATTERY_COMMAND):
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
        self._sp_last_call = 0
        self._td_up = None
        self._td_cap = 0.0
        self._td_eng = 0.0
        self._td_eng_lock = threading.Lock()

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

    @property
    def current_now_milis(self) -> float:
        """Retorna a velocidade da (des)carga em mA"""
        self.refresh()
        return self._current_now_milis

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

    def _emulator(self, perc_start: float, cap: float):
        self._td_eng_lock.acquire()
        self._td_eng = perc_start * cap
        self._td_cap = cap
        self._td_up = True
        self._td_eng_lock.release()

        i = time.perf_counter()
        pi = i
        while self._td_up:
            cur = self.current_now_milis
            self._td_eng_lock.acquire()
            i = time.perf_counter()

            # mA*s -> mA*h: s/3600
            self._td_eng += cur*(i-pi)/3600
            self._td_eng_lock.release()

            time.sleep(DRIVER_SLEEP)
            pi = i

    def start_emulating_cap(self, cap: float, perc_start: int = LEVEL_LOW):
        """
        Inicia o emulador do MoniBat.

        ### Parâmetro obrigatório:
         - cap [float]: capacidade em Ah;
        ### Parâmetro opcional:
         - perc_start [int]: percentual para iniciar o emulador, como por exemplo: 50 (%).
        """
        if self._td_up is None or self._td_up:
            return
        f_perc_start = float(perc_start)/100
        cap *= 1000  # conversão para mAh
        self._td = threading.Thread(
            target=self._emulator, args=(f_perc_start, cap,))
        self._td.start()
        self._sp_last_call = 0
        while not self.done():
            pass

    def reset_cap(self):
        assert self._td_up == True
        self._td_eng_lock.acquire()
        self._td_eng = self._td_cap
        self._td_eng_lock.release()

    def stop_emulating_cap(self):
        if self._td_up:
            self._td_up = False
            self._td.join()

    def done(self):
        r = self._td_up
        if r:
            return r
        self._td_eng_lock.acquire()
        r = self._td_up
        self._td_eng_lock.release()
        return r


if __name__ == '__main__':
    battery = Battery()
    print(battery.percent)
    battery.start_emulating_cap(2.0, 50)
    print(battery.current_now)
    battery.stop_emulating_cap()
