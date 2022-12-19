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
MIN_VOLTAGE_TYP = 3.6

DEFAULT_SETTINGS = {
    "percent": {
        "empty": 0,
        "full": 100,
        "fix": False,
        "low": 20,
        "high": 80,
    },
    "voltage": {
        "empty": 3.4,
        "full": 4.2,
        "low": 3.7,
        "high": 4.1,
    },
    "temp": {
        "min": 5.0,
        "high": 40.0,
        "max": 55.0,
    }
}