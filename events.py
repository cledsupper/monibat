# Utilizado pelos módulos:
# eventloop

from config.tweaker import Configuration, DELAY_CHARGING, DELAY_DISCHARGING
import notify

cfg: Configuration = None


def install_config(m_cfg: Configuration):
    global cfg
    cfg = m_cfg
    cfg.reset_alarms()


def on_percent_increase(delta: int):
    percent = cfg.btweaks["percent"]

    if cfg.a_percent_low and percent >= cfg.data["percent"]["low"]:
        cfg.a_percent_low = False

    if cfg.a_percent_high:
        return

    status = cfg.btweaks["status"]
    if status == 'Charging' and percent >= cfg.data["percent"]["high"]:
        cfg.a_percent_high = True
        notify.send_message(
            'Desconecte o carregador para preservar a saúde da bateria',
            title='aviso de carga'
        )


def on_percent_decrease(delta: int):
    percent = cfg.btweaks["percent"]

    if cfg.a_percent_high and percent < cfg.data["percent"]["high"]:
        cfg.a_percent_high = False

    if cfg.a_percent_low:
        return

    status = cfg.btweaks["status"]
    if status == 'Discharging' and percent < cfg.data["percent"]["low"]:
        cfg.a_percent_low = True
        notify.send_message(
            'Conecte o carregador para preservar a saúde da bateria',
            title='bateria fraca 📉'
        )


def on_voltage_increase(delta: int):
    pass


def on_voltage_decrease(delta: int):
    pass


def on_temp_increase(delta: int):
    temp = cfg.btweaks["temp"]
    if cfg.a_temp_min and temp > cfg.data["temp"]["min"]:
        cfg.a_temp_min = False

    if cfg.a_temp_max:
        return

    if temp >= cfg.data["temp"]["max"]:
        cfg.a_temp_max = True
        notify.send_toast('📵 A BATERIA VAI EXPLODIR! 📵')
        notify.send_message(
            '📵 DESLIGUE O CELULAR AGORA! 📵',
            title='A BATERIA VAI EXPLODIR 🧨 🔥'
        )
        return

    if cfg.a_temp_hot:
        return

    if temp >= cfg.data["temp"]["hot"]:
        cfg.a_temp_hot = True
        notify.send_message(
            'Habilite a economia da energia para esfriar a bateria',
            title='aviso de temperatura'
        )


def on_temp_decrease(delta: int):
    temp = cfg.btweaks["temp"]
    if cfg.a_temp_hot and temp < cfg.data["temp"]["hot"]:
        cfg.a_temp_hot = False
        cfg.a_temp_max = False
    elif cfg.a_temp_max and temp < cfg.data["temp"]["max"]:
        cfg.a_temp_max = False

    if cfg.a_temp_min:
        return

    if temp <= cfg.data["temp"]["min"]:
        cfg.a_temp_min = True
        notify.send_message(
            'O desempenho da bateria deve piorar bastante! 📉',
            title='bateria gelada 🧊'
        )


def on_status_change(from_status: str):
    if cfg.btweaks['status'] == 'Charging':
        cfg.delay = DELAY_CHARGING
        notify.send_toast('O conector foi conectado 🔌🔋')
    else:
        cfg.delay = DELAY_DISCHARGING
        if cfg.btweaks['status'] == 'Discharging':
            if from_status == 'Full' or from_status == 'Charging':
                notify.send_toast('O conector foi desconectado 🔋')
    cfg.reset_alarms()
