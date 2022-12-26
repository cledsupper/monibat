# notify.py - MoniBat's event loop logic
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
# -> service

import sys
import time

from data.messages import *
from events import *


def batt_refresh():
    batt = cfg.batt
    bd = {}
    bd["status"] = batt.status()
    bd["percent"] = batt.percent()
    bd["energy"] = batt.energy_now()
    bd["capacity"] = batt.capacity()
    bd["current"] = batt.current_now()
    bd["temp"] = batt.temp()
    bd["voltage"] = batt.voltage()
    bd["technology"] = batt.technology()
    bd["health"] = batt.health()

    # TODO: tweak battery data here
    bd["percent"] = cfg.fix_percent(bd)
    bd["status"] = cfg.fix_status(bd)
    bd["level"] = 'Normal'
    if bd["percent"] == 100:
        bd["level"] = 'Full'
    elif bd["percent"] >= cfg.data["percent"]["high"]:
        bd["level"] = 'High'
    elif bd["percent"] < cfg.data["percent"]["low"]:
        bd["level"] = 'Low'
    elif bd["percent"] < 5:
        bd["level"] = 'Critical'

    return bd


def run_events():
    result = False
    btweaks = cfg.btweaks
    o_btweaks = cfg.o_btweaks

    dp = btweaks['percent'] - o_btweaks['percent']
    if dp != 0:
        if dp > 0:
            on_percent_increase(dp)
        else:
            on_percent_decrease(dp)
        result = True

    if btweaks['voltage'] and o_btweaks['voltage']:
        old = int(o_btweaks['voltage'] * 10)
        new = int(btweaks['voltage'] * 10)
        dv = old - new
        if dv != 0:
            if dv > 0:
                on_voltage_increase(dv)
            else:
                on_voltage_decrease(dv)
            result = True

    if btweaks['temp'] is not None:
        old = int(o_btweaks['temp'] * 10)
        new = int(btweaks['temp'] * 10)
        dt = old - new
        if dt != 0:
            if dt > 0:
                on_temp_increase(dt)
            else:
                on_temp_decrease(dt)
            result = True

    if btweaks['status'] != o_btweaks['status']:
        on_status_change(o_btweaks['status'])
        result = True

    # o_stnow = time.mktime(cfg.o_tnow)
    # stnow = time.mktime(cfg.tnow)
    # if (stnow - o_stnow) >= cfg.delay:
        # result = True

    return result


def iterate():
    cfg.tnow = time.localtime()

    cfg.o_btweaks = cfg.btweaks
    cfg.btweaks = batt_refresh()
    if cfg.data["capacity"] and not cfg.batt._td_up:
        notify.send_message(TERMUX_ERRORS_LIMIT_REACH)
        raise RuntimeError(TERMUX_ERRORS_LIMIT_REACH)

    status_refresh = False
    if cfg.o_btweaks:
        status_refresh = run_events()
    else:
        status_refresh = True

    if status_refresh:
        cfg.o_tnow = cfg.tnow
        if not notify.status_shown or cfg.btweaks["status"] != "Not charging":
            notify.send_status(cfg.btweaks)
        cfg.update()

    if cfg.btweaks["status"] == 'Not charging':
        time.sleep(DELAY_DISCHARGING)
    else:
        time.sleep(DELAY_CHARGING)


def cleanup():
    fcache = sys.stderr
    cfg.batt.stop_emulating_cap()
    sys.stdout = sys.o_stdout
    sys.stderr = sys.o_stderr
    fcache.close()


def handle_sigterm(sig, frame):
    notify.status_remove()
    notify.send_toast("encerrado")
    try:
        os.remove(FPID)
    except FileNotFoundError:
        pass
        sys.stderr = sys.o_stderr
    sys.stderr = sys.o_stderr
    cleanup()
    exit(0)
