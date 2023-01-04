# events.py - MoniBat's general set of alarms/events
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
# eventloop

import driver
from config.tweaker import *
import notify

cfg = Configuration(notify.send_toast)
notify.send_toast('Verificão da depuração ADB pode levar %d min' %
                  (SUBPROCESS_TIMEOUT/60))
cfg.batt = driver.Battery()
if cfg.data["capacity"]:
    cfg.batt.start_emulating_cap(
        cfg.data["capacity"],
        cfg.infer_percent(cfg.batt)
    )
cfg.delay = DELAY_CHARGING if cfg.batt.charging() else DELAY_DISCHARGING


def recalibrate_start():
    """Ação para calibrar a bateria quando da tensão discrepante à carga."""
    if cfg.calibrate or not (cfg.batt._td_up and cfg.btweaks["status"] == 'Discharging'):
        return False

    v = cfg.btweaks["voltage"]
    if v is None:
        return
    lv = cfg.data["voltage"]["low"]
    vtyp = str(cfg.data["voltage"]["typ"])
    p = cfg.btweaks["percent"]
    lp = LEVEL_LOW_BY_VOLTAGE_TYP[vtyp]

    if (v >= lv-0.05 and v < lv) and abs(p-lp) >= 5:
        cfg.calibrate = True
        cfg.batt.stop_emulating_cap()
        cfg.batt.start_emulating_cap(
            cfg.data["capacity"],
            perc_start=lp
        )
        cfg.calibrate_aux = (lp * cfg.data["capacity"])/100

        notify.send_message(
            'carregue a bateria completamente para concluir',
            title='calibração da bateria iniciada ℹ',
            icon='battery_alert'
        )
        return True

    return False

def recalibrate_finish():
    if not cfg.calibrate:
        return False

    cfg.calibrate = False
    vtyp = str(self.data["voltage"]["typ"])
    chgd = cfg.btweaks["energy"] - cfg.calibrate_aux
    cfg.data["capacity"] = chgd / \
        (float(100 - LEVEL_LOW_BY_VOLTAGE_TYP[vtyp])/100.0)
    cfg.save()
    cfg.batt.stop_emulating_cap()
    cfg.batt.start_emulating_cap(
        cfg.data["capacity"],
        perc_start=100
    )
    notify.send_message(
        'resultado: %0.2f Ah' % (cfg.data["capacity"]),
        title='bateria calibrada! ✅'
    )
    return True


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
    if recalibrate_start():
        return

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
    recalibrate_start()

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
            title='A BATERIA VAI EXPLODIR 🧨 🔥',
            icon='hot_tub'
        )
        return

    if cfg.a_temp_hot:
        return

    if temp >= cfg.data["temp"]["hot"]:
        cfg.a_temp_hot = True
        if cfg.btweaks["status"] == 'Discharging':
            notify.send_message(
                'Habilite a economia da energia para esfriar a bateria',
                title='aviso de temperatura',
                icon='battery_alert'
            )
        else:
            notify.send_message(
                'Desconecte o carregador para esfriar a bateria',
                title='aviso de temperatura',
                icon='battery_alert'
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
            title='bateria gelada 🧊',
            icon='ac_unit'
        )


def on_status_change(from_status: str):
    if cfg.btweaks['status'] == 'Charging':
        cfg.delay = DELAY_CHARGING
        if from_status == 'Not charging' or from_status == 'Full':
            notify.send_toast('O conector foi conectado 🔌🔋')
    elif cfg.btweaks["status"] == 'Full':
        cfg.delay = DELAY_DISCHARGING
        if not recalibrate_finish() and cfg.batt._td_up:
            if int(cfg.btweaks["capacity"]*1000) != int(cfg.btweaks["energy"]*1000):
                cfg.batt.reset_cap()
    else:
        cfg.delay = DELAY_DISCHARGING
        if cfg.btweaks['status'] == 'Discharging':
            if from_status == 'Full' or from_status == 'Charging':
                notify.send_toast('O conector foi desconectado 🔋')
    cfg.reset_alarms()
