# driver.py - Interface de leitura da bateria para termux-battery-status
import json
import os
import subprocess
import time
from typing import Optional

from config.constants import DEFAULT_DIRPATH, DELAY_CHARGING, DELAY_SUBPROCESS

def to_linux_str(termux_str: str) -> str:
    return termux_str[0] + termux_str[1:].lower().replace('_', ' ')

tmp = os.getenv('DEFAULT_DIRPATH')
if tmp:
    try:
        subprocess.run([tmp], check=True, timeout=DELAY_SUBPROCESS)
    except:
        print('#error Comando inválido: "%s"' % (tmp))
        raise RuntimeError('error when tried to run DEFAULT_DIRPATH')
    else:
        DEFAULT_DIRPATH = tmp


class Battery:
    """Classe Battery para acessar informações da bateria"""
    def __init__(self, dirpath: str = DEFAULT_DIRPATH, check_unit: bool = True):
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
        self.check_call()

    def check_call(self):
        """Pula múltiplas chamadas à Termux:API até um tempo específico: DELAY_CHARGING."""
        tnow = time.time()
        td = tnow - self._sp_last_call
        if td < DELAY_CHARGING:
            return
        self._sp_last_call = tnow

        proc = subprocess.run(
            [self._cmd],
            capture_output=True,
            check=True
        )
        text = proc.stdout.decode()
        self._sp_data = json.loads(text)

    def _get_sp_data(self, key: str):
        """Retorna o dado solicitado pela verificação do tempo para atualização dos dados."""
        self.check_call()
        return self._sp_data[key]

    def get_unit(self) -> str:
        """Retorna a unidade ((A)mpère ou (W)atts) das medições de consumo elétrico."""
        if not self._unit_checked: self._unit_checked = True
        return 'A'

    def percent(self) -> int:
        """Nível de carga da bateria em percentual"""
        return self._get_sp_data('percentage')

    def charging(self) -> bool:
        """A bateria está carregando?"""
        return self._get_sp_data('status') == 'CHARGING'

    def capacity(self) -> Optional[float]:
        """Retorna a capacidade estimada da bateria em Watts ou Amperes"""
        return None

    def capacity_design(self) -> Optional[float]:
        """Retorna a capacidade típica da bateria em Watts ou Amperes"""
        return None

    def energy_now(self) -> Optional[float]:
        """Retorna o nível de carga da bateria em Watts ou Amperes"""
        return None

    def current_now(self) -> Optional[float]:
        """Retorna a velocidade da (des)carga em Watts ou Amperes"""
        return self._get_sp_data('current') / 1000

    def temp(self) -> Optional[float]:
        """Temperatura da bateria (ºC)"""
        return self._get_sp_data('temperature')

    def voltage(self) -> Optional[float]:
        """Tensão da bateria (V)"""
        return None

    def health(self) -> Optional[str]:
        """Saúde da bateria"""
        value = self._get_sp_data('health')
        return to_linux_str(value)

    def technology(self) -> Optional[str]:
        """Tecnologia da bateria (Li-ion, Li-poly, etc.)"""
        return None

    def status(self) -> Optional[str]:
        """Status da bateria: Charging, Discharging, Unknown, ..."""
        value = self._get_sp_data('status')
        return to_linux_str(value)

if __name__ == '__main__':
    battery = Battery()
    technology = battery.technology()
    if technology is not None:
        print('Battery ' + technology)
    else:
        print('Battery')
    print('%d %%' % (battery.percent()))
    print(battery.health())
