# batteryemulator.py - MoniBat Capacity Counter
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

import threading
import time

from batteryinterface import BatteryInterface, Optional
from config.constants import DRIVER_SLEEP, LEVEL_LOW


class BatteryEmulator(BatteryInterface):
    def __init__(self, cap: Optional[float] = None):
        """
        Construtor do emulador.

        ### Parâmetro opcional:
        - cap [float | None]: capacidade típica em Ampère-hora (Ah)
        """
        self._capacity = cap
        self._capacity_design = cap

        self._td_zero = 10*cap if cap else 20.0
        """Corrente insignificante em (mA). É sempre 1% da capacidade típica ou 20 mA."""
        self._zero = self._td_zero / 1000

        self._td_up: Optional[bool] = None
        """Se o emulador está ativo. None significa que não há suportado"""

        self._td_cap = 0.0
        """Capacidade em (mAh)"""

        self._td_eng = 0.0
        """Energia em (mAh)"""

        self._td_eng_lock = threading.Lock()
        """Bloqueie para alterar qualquer variável do emulador"""

    @property
    def current_now_milis(self) -> float:
        """Retorna a velocidade da (des)carga em mA"""
        self.refresh()
        return self._current_now_milis

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
        if self._td_up or self._td_up is None:
            return
        f_perc_start = float(perc_start)/100
        self._capacity = cap
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
            self.driver_stop()

    def done(self):
        r = self._td_up
        if r:
            return r
        self._td_eng_lock.acquire()
        r = self._td_up
        self._td_eng_lock.release()
        return r
