# Utilizado pelos módulos:
# -> service

import sys
import time

import driver


from config.tweaker import Configuration, FPID, DELAY_CHARGING, DELAY_DISCHARGING, os

from events import *

cfg = Configuration(notify.send_toast)
cfg.batt = driver.Battery()
install_config(cfg)

def tweaks():
  batt = cfg.batt
  bd = {}
  bd["percent"] = batt.percent()
  bd["status"] = batt.status()
  bd["current"] = batt.current_now()
  bd["temp"] = batt.temp()
  bd["voltage"] = batt.voltage()
  bd["technology"] = batt.technology()
  bd["health"] = batt.health()

  cap = cfg.data["capacity"]
  if cap:
    if cfg.charge is None or bd["status"] == 'Full':
      cfg.charge = bd["percent"]*cap / 100
    else:
      cfg.charge += bd["current"]*cfg.xch
    bd["charge"] = cfg.charge

  # TODO: tweak battery data here
  bd["percent"] = cfg.fix_percent(bd)
  bd["status"] = cfg.fix_status(bd)

  return bd

cfg.o_tnow = None
cfg.tnow = None
cfg.btweaks = None
cfg.o_btweaks = None

cfg.delay = DELAY_CHARGING if cfg.batt.charging() else DELAY_DISCHARGING

def run_events():
  result = False
  btweaks = cfg.btweaks
  o_btweaks = cfg.o_btweaks

  dp = btweaks['percent'] - o_btweaks['percent']
  if dp != 0:
    if dp > 0: on_percent_increase(dp)
    else: on_percent_decrease(dp)
    result = True

  if btweaks['voltage'] is not None:
    old = int(o_btweaks['voltage'] * 10)
    new = int(btweaks['voltage'] * 10)
    dv = old - new
    if dv != 0:
      if dv > 0: on_voltage_increase(dv)
      else: on_voltage_decrease(dv)
      result = True

  if btweaks['temp'] is not None:
    old = int(o_btweaks['temp'] * 10)
    new = int(btweaks['temp'] * 10)
    dt = old - new
    if dt != 0:
      if dt > 0: on_temp_increase(dt)
      else: on_temp_decrease(dt)
      result = True
  
  if btweaks['status'] != o_btweaks['status']:
    on_status_change(o_btweaks['status'])
    result = True

  o_stnow = time.mktime(cfg.o_tnow)
  stnow = time.mktime(cfg.tnow)
  if (stnow - o_stnow) >= cfg.delay:
    result = True

  return result

def iterate():
  cfg.tnow = time.localtime()

  cfg.o_btweaks = cfg.btweaks
  cfg.btweaks = tweaks()

  status_refresh = False
  if cfg.o_btweaks:
    status_refresh = run_events()
  else:
    status_refresh = True

  if status_refresh:
    cfg.o_tnow = cfg.tnow
    if cfg.btweaks["status"] != "Not charging":
      notify.send_status(cfg.btweaks)
    cfg.update()

  if cfg.btweaks["status"] == 'Not charging':
    time.sleep(DELAY_DISCHARGING)
  else:
    time.sleep(DELAY_CHARGING)

def handle_sigterm(sig, frame):
  notify.status_remove()
  notify.send_toast("encerrado")
  try:
    os.remove(FPID)
  except FileNotExistsError:
    pass
  fcache = sys.stderr
  sys.stdout = sys.o_stdout
  sys.stderr = sys.o_stderr
  fcache.close()
  exit(0)
