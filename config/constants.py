# Utilizado pelos módulos:
# -> tweaker, driver, events

# Comando para obter o JSON com o estado da bateria
BATTERY_DIRPATH = 'termux-battery-status'

SUBPROCESS_TIMEOUT=7

DELAY_CHARGING = 6
DELAY_DISCHARGING = 60

TERMUX_ERRORS_LIMIT = 15

# DESIGN: propagar estes limites na interface!
MIN_LEVEL_EMPTY = 0
MAX_LEVEL_FULL = 100

# É bom que seja bateria de lítio
VOLTAGE_TYP = 3.6
VOLTAGE_EMPTY = 3.4
VOLTAGE_FULL = 4.2

TEMP_MIN = 5.0
TEMP_HOT = 40.0
TEMP_MAX = 55.0

DEFAULT_SETTINGS = {
    "percent": {
        "empty": 0,
        "full": 100,
        "fix": False,
        "low": 20,
        "high": 80,
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