# Utilizado pelos módulos:
# -> batttweaker
# -> driver

DEFAULT_SETTINGS = {
    'level_min': 0,
    'level_max': 100,
    'level_fix': False,
    # voltage_typ é opcional
    'voltage_typ': None
}

DELAY_CHARGING = 6
DELAY_DISCHARGING = 60

# DESIGN: propagar estes limites na interface!
MIN_LEVEL_MIN = 0
# Normalmente a bateria está a ponto de estufar
MAX_LEVEL_MIN = 70
# Porém jamais level_min >= level_max!
MIN_LEVEL_MAX = 50
MAX_LEVEL_MAX = 100
# É bom que seja bateria de lítio
MIN_VOLTAGE_TYP = 3.6
