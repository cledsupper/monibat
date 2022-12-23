# constants.py - Various values used in MoniBat source code
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
BATTERY_DIRPATH = 'termux-battery-status'

SUBPROCESS_TIMEOUT = 60

DELAY_CHARGING = 6
DELAY_DISCHARGING = 60

TERMUX_ERRORS_LIMIT = 15

LEVEL_EMPTY = 0
LEVEL_FULL = 100
LEVEL_LOW = 20
LEVEL_HIGH = 80

# É bom que seja bateria de lítio
VOLTAGE_TYP = 3.7
VOLTAGE_EMPTY = 3.4
VOLTAGE_FULL = 4.2

TEMP_MIN = 5.0
TEMP_HOT = 40.0
TEMP_MAX = 55.0

DEFAULT_SETTINGS = {
    "capacity": 0.0,
    "percent": {
        "empty": LEVEL_EMPTY,
        "full": LEVEL_FULL,
        "fix": False,
        "low": LEVEL_LOW,
        "high": LEVEL_HIGH,
    },
    "voltage": {
        "empty": VOLTAGE_EMPTY,
        "full": VOLTAGE_FULL,
        "low": VOLTAGE_TYP,
        "high": VOLTAGE_FULL,
    },
    "temp": {
        "min": TEMP_MIN,
        "hot": TEMP_HOT,
        "max": TEMP_MAX,
    }
}
