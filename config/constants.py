# constants.py - Various values used in MoniBat source code
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
# -> tweaker, driver

import os

APP_NAME = 'MoniBat'

APP_PID = os.getpid()

LIB = os.path.join(os.environ['PREFIX'], 'lib', APP_NAME)

APP_PY = os.path.join(LIB, 'service.py')


# $HOME/.config/Notify-Py
# PRESTE A ATENÇÃO A ALTERAR O NOME DESTE DIRETÓRIO
CONFIG = os.path.join(os.environ['HOME'], '.config', APP_NAME)
# $HOME/.config/Notify-Py/app.conf
# ESTA B****A DEPENDE DA VARIÁVEL ANTERIOR!!!
FCONFIG = os.path.join(CONFIG, 'config.json')

CACHE = os.path.join(os.environ['HOME'], '.cache', APP_NAME)

FCACHE = os.path.join(CACHE, 'logs.txt')

FPID = os.path.join(CACHE, 'instance.pid')

# Comando para obter o JSON com o estado da bateria
BATTERY_COMMAND = 'termux-battery-status'

SUBPROCESS_TIMEOUT = 60

# Limites de descarga para iniciar a calibração da bateria
BATTERY_SAVE_C_MIN = 0.03  # Coulomb: 0,03*5000 = 150 mA
BATTERY_SAVE_C_MAX = 0.13  # ... = 650 mA

# Maior corrente possível (65 W / 5 V ≃ 13.000 mAh)
DRIVER_CURRENT_MAX = 13000.0

DRIVER_SLEEP = 6.0
DELAY_CHARGING = 6
DELAY_DISCHARGING = 60

INDENTATION_DEFAULT = 4

LEVEL_EMPTY = 0
# Corrigir percentual vazio (inclusive do emulador)
LEVEL_FULL = 100
# Corrigir percentual cheio (inclusive do emulador)
LEVEL_FIX = False
# Corrigir percentual? padrão: não.
LEVEL_LOW = 15
# Exibir notificação quando a bateria estiver em 15 %.
LEVEL_HIGH = 80
# Exibir notificação quando a bateria estiver em 80 %.

LEVEL_LOW_BY_VOLTAGE_TYP = {
    '3.7': 30,
    '3.8': 20,
    '3.85': 15,
    # 20 % é reforçado pelo estado de descarga até 0,13 C em três dispositivos diferentes: POCO M5s, Ideapad 3 e Galaxy A20 (casos excepcionais), mas, por segurança, manterei em 15 %.

    '3.9': 15
    # estado de descarga do POCO M5s em até 0,13 C retorna 3,7 V em 20 %, mas por segurança, vou manter em 15 %.

    # NOTE: caso necessário, adicione a tensão típica da sua bateria!
}

LEVEL = {
    "Critical": "reserva de emergência",
    "Low": "fraca",
    "Normal": "normal",
    "High": "carregada",
    "Full": "completa"
}

# É bom que seja bateria de lítio
VOLTAGE_TYP = 3.9
# Tensão nominal da bateria.
VOLTAGE_EMPTY = 3.4
# Tensão mínima para o dispositivo funcionar.
VOLTAGE_LOW = 3.7
# VOLTAGE_LOW não deve ser alterado a menos que a bateria seja um pack de células ligadas em série. Neste caso, multiplique.
VOLTAGE_FULL = 4.55
# VOLTAGE_FULL corresponde à tensão máxima de carregamento suportado pela bateria.
VOLTAGE_HIGH = 4.4
# VOLTAGE_HIGH corresponde à tensão reportada pela bateria quando está em 100 % e descarregando.

TEMP_MIN = 5.0
TEMP_HOT = 40.0
TEMP_MAX = 55.0

DEFAULT_SETTINGS = {
    "capacity": 0.0,
    "capacity_design": 0.0,
    "infer_percent_always": False,
    "adb_reflect": False,
    "percent": {
        "empty": LEVEL_EMPTY,
        "full": LEVEL_FULL,
        "fix": LEVEL_FIX,
        "low": LEVEL_LOW,
        "high": LEVEL_HIGH
    },
    "voltage": {
        "empty": VOLTAGE_EMPTY,
        "full": VOLTAGE_FULL,
        # NÃO CONFUNDA ESTES VALORES COM SEUS RESPECTIVOS EM "percent"!
        "low": VOLTAGE_LOW,
        "high": VOLTAGE_FULL,
        "typ": VOLTAGE_TYP
    },
    "temp": {
        "min": TEMP_MIN,
        "hot": TEMP_HOT,
        "max": TEMP_MAX
    }
}

CALIBRATION_STATE_NONE = 0
CALIBRATION_STATE_START = 1
CALIBRATION_STATE_PARTIAL = 2
CALIBRATION_STATE_MANUAL = 3
CALIBRATION_STATE_FINAL = 4

CALIBRATION_MAX_ERROR = 5

RECALIBRATION_IDLE_TIME = 1800.0

ADB_STATUS = {
    'Unknown': 1,
    'Charging': 2,
    'Discharging': 3,
    'Not charging': 4,
    'Full': 5
}
