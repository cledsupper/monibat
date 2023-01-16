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
import sys

cfg = Configuration(notify.send_toast)
notify.send_toast(EVENTS_ADB_CHECK_WARNING % (SUBPROCESS_TIMEOUT))
cfg.batt = driver.Battery()
if cfg.data["capacity"]:
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        cfg.batt.start_emulating_cap(cfg.data["capacity"], int(sys.argv[1]))
    else:
        cfg.batt.start_emulating_cap(
            cfg.data["capacity"],
            cfg.infer_percent(cfg.batt)
        )
cfg.delay = DELAY_CHARGING if cfg.batt.charging() else DELAY_DISCHARGING


def recalibrate_start(lp):
    """Início do processo de calibração: marca o emulador em nível padrão de baixa tensão conforme a tensão nominal da bateria."""
    cfg.calibrated = CALIBRATION_STATE_START
    cfg.calibrate_aux = (lp * cfg.data["capacity"])/100

    notify.send_message(
        EVENTS_RECALIBRATE_START_MESSAGE,
        title=EVENTS_RECALIBRATE_START_TITLE,
        icon='battery_alert'
    )
    return cfg.data["capacity"]


def recalibrate_finish():
    """Passo final para salvar a capacidade real (utilizável) da bateria."""
    cfg.calibrated = CALIBRATION_STATE_FINAL
    cfg.save()
    notify.send_message(
        EVENTS_RECALIBRATE_FINISH_MESSAGE % (cfg.data["capacity"]),
        title=EVENTS_RECALIBRATE_FINISH_TITLE
    )
    return True


def recalibrate_partial(dp):
    """Quando já foi obtida uma estimativa de capacidade real e se obteve um erro, corrigir."""
    cap = cfg.data["capacity"]
    cap = cap*(1+dp/100)
    cfg.data["capacity"] = cap
    recalibrate_finish()
    return cap


def recalibrate_on_discharge():
    """Ação para calibrar a bateria quando da tensão discrepante à carga."""
    if cfg.calibrated == CALIBRATION_STATE_START:
        return False
    elif not (cfg.batt._td_up and cfg.btweaks["status"] == 'Discharging'):
        return False

    v = cfg.btweaks["voltage"]
    if v is None:
        return
    lv = cfg.data["voltage"]["low"]
    vtyp = str(cfg.data["voltage"]["typ"])
    p = cfg.btweaks["percent"]
    lp = LEVEL_LOW_BY_VOLTAGE_TYP[vtyp]
    dp = lp-p

    if (v >= lv-0.02 and v < lv):
        if abs(dp) >= 5:
            cap = cfg.data["capacity"]
            if cfg.calibrated == CALIBRATION_STATE_NONE:
                cap = recalibrate_start(lp)
            elif cfg.calibrated == CALIBRATION_STATE_PARTIAL:
                cap = recalibrate_partial(dp)

            cfg.batt.stop_emulating_cap()
            cfg.batt.start_emulating_cap(cap, perc_start=lp)
            return True

        elif cfg.calibrated == CALIBRATION_STATE_PARTIAL:
            return recalibrate_finish()

    elif abs(dp) < 5 and cfg.calibrated == CALIBRATION_STATE_PARTIAL:
        return recalibrate_finish()

    return False


def recalibrate_on_full():
    """Passo da calibração parcial da bateria: estima a capacidade real após a carga completa desde a baixa tensão."""
    if cfg.calibrated != CALIBRATION_STATE_START:
        return False
    cfg.calibrated = CALIBRATION_STATE_PARTIAL

    vtyp = str(cfg.data["voltage"]["typ"])
    low = LEVEL_LOW_BY_VOLTAGE_TYP[vtyp]
    chgd = cfg.btweaks["energy"] - cfg.calibrate_aux
    cfg.data["capacity"] = chgd / (float(100 - low)/100.0)
    cfg.save()
    cfg.batt.stop_emulating_cap()
    cfg.batt.start_emulating_cap(
        cfg.data["capacity"],
        perc_start=100
    )
    notify.send_message(
        EVENTS_RECALIBRATE_PARTIAL_MESSAGE % (low),
        title=EVENTS_RECALIBRATE_PARTIAL_TITLE
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
            EVENTS_ALARM_PERCENT_HIGH_MESSAGE,
            title=EVENTS_ALARM_PERCENT_TITLE
        )


def on_percent_decrease(delta: int):
    if recalibrate_on_discharge():
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
            EVENTS_ALARM_PERCENT_LOW_MESSAGE,
            title=EVENTS_ALARM_PERCENT_LOW_TITLE
        )


def on_voltage_increase(delta: int):
    pass


def on_voltage_decrease(delta: int):
    recalibrate_on_discharge()


def on_temp_increase(delta: int):
    temp = cfg.btweaks["temp"]
    if cfg.a_temp_min and temp > cfg.data["temp"]["min"]:
        cfg.a_temp_min = False

    if cfg.a_temp_max:
        return

    if temp >= cfg.data["temp"]["max"]:
        cfg.a_temp_max = True
        notify.send_toast(EVENTS_ALARM_TEMPERATURE_MAX_TOAST)
        notify.send_message(
            EVENTS_ALARM_TEMPERATURE_MAX_MESSAGE,
            title=EVENTS_ALARM_TEMPERATURE_MAX_TITLE,
            icon='hot_tub'
        )
        return

    if cfg.a_temp_hot:
        return

    if temp >= cfg.data["temp"]["hot"]:
        cfg.a_temp_hot = True
        if cfg.btweaks["status"] == 'Discharging':
            notify.send_message(
                EVENTS_ALARM_TEMPERATURE_HIGH_WHEN_DISCHARGING,
                title=EVENTS_ALARM_TEMPERATURE_TITLE,
                icon='battery_alert'
            )
        else:
            notify.send_message(
                EVENTS_ALARM_TEMPERATURE_HIGH_WHEN_CHARGING,
                title=EVENTS_ALARM_TEMPERATURE_TITLE,
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
            EVENTS_ALARM_TEMPERATURE_MIN_MESSAGE,
            title=EVENTS_ALARM_TEMPERATURE_TITLE,
            icon='ac_unit'
        )


def on_status_change(from_status: str):
    if cfg.btweaks['status'] == 'Charging':
        cfg.delay = DELAY_CHARGING
    elif cfg.btweaks["status"] == 'Full':
        cfg.delay = DELAY_DISCHARGING
        if not recalibrate_on_full() and cfg.batt._td_up:
            cfg.batt.reset_cap()
    else:
        cfg.delay = DELAY_DISCHARGING
    cfg.reset_alarms()
