# Utilizado pelos módulos:
# -> service.py

import time

import driver
import notify

from config.constants import DELAY_CHARGING, DELAY_DISCHARGING
from config.tweaker import Configuration

batt = driver.Battery()
cfg = Configuration()

def tweaks():
  global batt
  bd = {}
  bd["percent"] = batt.percent()
  bd["status"] = batt.status()
  bd["current"] = batt.current_now()
  bd["temp"] = batt.temp()
  bd["voltage"] = batt.voltage()
  bd["technology"] = batt.technology()
  bd["health"] = batt.health()
  
  # TODO: tweak battery data here

  return bd

day = None
now = None
btweaks = None
o_btweaks = None

delay = DELAY_DISCHARGING

def on_percent_increase(btweaks: dict, delta: int):
  pass

def on_percent_decrease(btweaks: dict, delta: int):
  pass

def on_voltage_increase(btweaks: dict, delta: int):
  pass

def on_voltage_decrease(btweaks: dict, delta: int):
  pass

def on_temp_increase(btweaks: dict, delta: int):
  pass

def on_temp_decrease(btweaks: dict, delta: int):
  pass

def on_status_change(btweaks: dict, from_status: str):
  global delay
  if btweaks['status'] == 'Charging':
    delay = DELAY_CHARGING
  else:
    delay = DELAY_DISCHARGING

def run():
  global day
  global now
  global btweaks
  global o_btweaks

  cfg.update()

  now = time.localtime()
  if day is None or now.tm_mday != day.tm_mday:
    day = now

  o_btweaks = btweaks
  btweaks = tweaks()

  # TODO: run events here
  status_refresh = False
  
  if o_btweaks is None:
    status_refresh = True

  else:
    dp = btweaks['percent'] - o_btweaks['percent']
    if dp != 0:
      if dp > 0: on_percent_increase(btweaks, dp)
      else: on_percent_decrease(btweaks, dp)
      status_refresh = True

    if btweaks['voltage'] is not None:
      old = int(o_btweaks['voltage'] * 10)
      new = int(btweaks['voltage'] * 10)
      dv = old - new
      if dv != 0:
        if dv > 0: on_voltage_increase(btweaks, dv)
        else: on_voltage_decrease(btweaks, dv)
        status_refresh = True

    if btweaks['temp'] is not None:
      old = int(o_btweaks['temp'] * 10)
      new = int(btweaks['temp'] * 10)
      dt = old - new
      if dt != 0:
        if dt > 0: on_temp_increase(btweaks, dt)
        else: on_temp_decrease(btweaks, dt)
        status_refresh = True
  
    if btweaks['status'] != o_btweaks['status']:
      on_status_change(btweaks, o_btweaks['status'])
      status_refresh = True

    sday = time.mktime(day)
    snow = time.mktime(now)
    if (snow - sday) >= delay:
      day = now
      status_refresh = True

  if status_refresh:
    notify.send_status(btweaks)

  time.sleep(1)
  return True