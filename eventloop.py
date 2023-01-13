# notify.py - MoniBat's event loop logic
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
# -> service

import time

from events import *


def batt_refresh():
    batt = cfg.batt
    bd = {
        "status": batt.status(),
        "percent": batt.percent(),
        "energy": batt.energy_now(),
        "capacity": batt.capacity(),
        "current": batt.current_now(),
        "temp": batt.temp(),
        "voltage": batt.voltage(),
        "technology": batt.technology(),
        "health": batt.health(),
        "level": 'Normal',
        "scale": None
    }

    if cfg.data["capacity_design"] and cfg.data["capacity_design"] != bd["capacity"]:
        bd["scale"] = bd["capacity"] / cfg.data["capacity_design"]

    bd["percent"] = cfg.fix_percent(bd)
    bd["status"] = cfg.fix_status(bd)
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
    if dp:
        if dp > 0:
            on_percent_increase(dp)
        else:
            on_percent_decrease(dp)
        result = True

    if btweaks['voltage'] and o_btweaks['voltage']:
        old = int(o_btweaks['voltage'] * 10)
        new = int(btweaks['voltage'] * 10)
        dv = new - old
        if dv:
            if dv > 0:
                on_voltage_increase(dv)
            else:
                on_voltage_decrease(dv)
            result = True

    if btweaks['temp'] is not None:
        old = int(o_btweaks['temp'] * 10)
        new = int(btweaks['temp'] * 10)
        dt = new - old
        if dt:
            if dt > 0:
                on_temp_increase(dt)
            else:
                on_temp_decrease(dt)
            result = True

    if btweaks['status'] != o_btweaks['status']:
        on_status_change(o_btweaks['status'])
        cfg.chg_perc = btweaks['percent']
        cfg.chg_time = cfg.tnow
        result = True

    return result


def calc_remaining_time():
    bd = cfg.btweaks
    # | agora - antes |
    pp = abs(bd['percent'] - cfg.chg_perc)
    if pp > 2:
        stnow = time.mktime(cfg.tnow)  # agora
        stchg = time.mktime(cfg.chg_time)  # antes
        s = stnow - stchg  # tempo dos N pontos percs.
        t = 0
        if bd['status'] != 'Charging':
            # tempo para descarregar
            t = bd['percent']*s/pp
        else:
            # tempo para carregar
            t = (100-bd['percent'])*s/pp
        return time.gmtime(int(t))
    return None


def iterate():
    cfg.tnow = time.localtime()

    cfg.o_btweaks = cfg.btweaks
    cfg.btweaks = batt_refresh()

    status_refresh = False
    if cfg.o_btweaks:
        status_refresh = run_events()
    else:
        status_refresh = True
        cfg.chg_perc = cfg.btweaks['percent']
        cfg.chg_time = cfg.tnow

    if status_refresh:
        cfg.o_tnow = cfg.tnow
        if not notify.status_shown or cfg.btweaks["status"] != "Not charging":
            remaining_time = calc_remaining_time()
            notify.send_status(cfg.btweaks, remaining_time)

    if cfg.update():
        if cfg.data["capacity"]:
            cfg.batt.start_emulating_cap(
                cfg.data["capacity"],
                perc_start=cfg.btweaks["percent"]
            )
        else:
            cfg.batt.stop_emulating_cap()

    time.sleep(cfg.delay)


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
