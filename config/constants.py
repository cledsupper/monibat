# Utilizado pelos módulos:
# -> driver, events.py

# Comando para obter o JSON com o estado da bateria
BATTERY_DIRPATH = 'termux-battery-status'

SUBPROCESS_TIMEOUT=7

DELAY_CHARGING = 6
DELAY_DISCHARGING = 60

TERMUX_ERRORS_LIMIT = 15

# DESIGN: propagar estes limites na interface!
MIN_LEVEL_MIN = 0
# Normalmente a bateria está a ponto de estufar
MAX_LEVEL_MIN = 70
# Porém jamais level_min >= level_max!
MIN_LEVEL_MAX = 50
MAX_LEVEL_MAX = 100
# É bom que seja bateria de lítio
MIN_VOLTAGE_TYP = 3.6
