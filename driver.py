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
import os
import shlex
import subprocess
import time
import threading
from typing import Optional

from config.constants import BATTERY_DIRPATH, DRIVER_SLEEP, LEVEL_LOW, SUBPROCESS_TIMEOUT


def to_linux_str(termux_str: str) -> str:
    return termux_str[0] + termux_str[1:].lower().replace('_', ' ')


class Battery:
    """Classe Battery para acessar informações da bateria"""

    # NOTE: rendiix has an ADB fork for Galaxy devices which actually works
    HAVE_ADB = False

    def __init__(self, dirpath: str = BATTERY_DIRPATH, check_unit: bool = True):
        try:
            subprocess.run(
                shlex.split('adb wait-for-device'),
                check=True,
                timeout=SUBPROCESS_TIMEOUT
            )
            Battery.HAVE_ADB = True
        except:
            pass
        self._cmd = dirpath
        self._unit_checked = check_unit
        self._sp_last_call = 0
        self._sp_data = {
            'percentage': -1,
            'health': 'BAD',
            'status': 'UNKNOWN',
            'temperature': 0.0,
            'current': 0.0,
            'plugged': 'UNPLUGGED'
        }
        self._td_up = False
        self._td_cap = None
        self._td_perc_start = float(LEVEL_LOW)
        self._td_eng = None
        self._td_eng_lock = threading.Lock()
        self._td = None
        self.check_call()

    def check_call(self):
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
            except subprocess.TimeoutExpired:
                pass

        text = proc.stdout
        self._sp_data = json.loads(text)

    def _get_sp_data(self, key: str):
        """Retorna o dado solicitado pela verificação do tempo para atualização dos dados."""
        self.check_call()
        return self._sp_data[key]

    def get_unit(self) -> str:
        """Retorna a unidade ((A)mpère ou (W)atts) das medições de consumo elétrico."""
        if not self._unit_checked:
            self._unit_checked = True
        return 'A'

    def percent(self) -> int:
        """Nível de carga da bateria em percentual"""
        if self._td_up:
            return 1+int(100 * self._td_eng / self._td_cap)
        return self._get_sp_data('percentage')

    def charging(self) -> bool:
        """A bateria está carregando?"""
        return self._get_sp_data('status') == 'CHARGING'

    def capacity(self) -> Optional[float]:
        """Retorna a capacidade estimada da bateria em Watts ou Amperes"""
        return self._td_cap

    def capacity_design(self) -> Optional[float]:
        """Retorna a capacidade típica da bateria em Watts ou Amperes"""
        return None

    def energy_now(self) -> Optional[float]:
        """Retorna o nível de carga da bateria em Watts ou Amperes"""
        return self._td_eng

    def current_now(self) -> Optional[float]:
        """Retorna a velocidade da (des)carga em Watts ou Amperes"""
        return self._get_sp_data('current') / 1000

    def temp(self) -> Optional[float]:
        """Temperatura da bateria (ºC)"""
        return self._get_sp_data('temperature')

    def voltage(self) -> Optional[float]:
        """Tensão da bateria (V)"""
        value = None
        if Battery.HAVE_ADB:
            try:
                proc = subprocess.run(
                    shlex.split(
                        'adb shell cat /sys/class/power_supply/battery/voltage_avg'
                    ),
                    capture_output=True,
                    check=True,
                    timeout=DRIVER_SLEEP
                )
                value = int(proc.stdout.decode().strip())
                value = float(value)/1000000.0
            except:
                pass
        return value

    def health(self) -> Optional[str]:
        """Saúde da bateria"""
        value = self._get_sp_data('health')
        return to_linux_str(value)

    def technology(self) -> Optional[str]:
        """Tecnologia da bateria (Li-ion, Li-poly, etc.)"""
        return None

    def status(self) -> str:
        """Status da bateria: Charging, Discharging, Unknown, ..."""
        value = self._get_sp_data('status')
        value = to_linux_str(value)
        return value

    def _cap_thread(self, cap: float):
        self._td_eng_lock.acquire()
        self._td_eng = self._td_perc_start * cap / 100
        self._td_cap = cap
        self._td_eng_lock.release()
        self._td_up = True

        i = 0.0
        while self._td_up:
            i = time.perf_counter()
            cur = self.current_now()
            self._td_eng_lock.acquire()
            i = time.perf_counter() - i

            # mA*s -> mA*h: s/3600
            self._td_eng += cur*(DRIVER_SLEEP+i)/3600
            self._td_eng_lock.release()

            time.sleep(DRIVER_SLEEP)

    def start_emulating_cap(self, cap: float, perc_start: int = LEVEL_LOW):
        if self._td_up:
            return
        self._td_perc_start = float(perc_start)
        self._td = threading.Thread(target=self._cap_thread, args=(cap,))
        self._td.start()

    def reset_cap(self):
        self._td_eng_lock.acquire()
        self._td_eng = self._td_cap
        self._td_eng_lock.release()

    def stop_emulating_cap(self):
        if self._td_up:
            self._td_up = False
            self._td.join()


if __name__ == '__main__':
    battery = Battery()
    battery.start_emulating_cap(2.0)
    time.sleep(7)
    eng = battery.energy_now()
    assert isinstance(eng, float)
    print('%0.2f' % (eng))
    battery.stop_emulating_cap()
    print('End')
