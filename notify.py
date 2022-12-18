# Utilizado pelos módulos:
# -> events.py

import subprocess
from typing import Optional

from config.constants import SUBPROCESS_TIMEOUT, TERMUX_ERRORS_LIMIT

tcount = TERMUX_ERRORS_LIMIT

def termux_api_call(
  message: str,
  icon = 'battery_std',
  title = 'estado da bateria',
  as_status = False,
  as_toast = False,
  as_error = False,
  as_fatal = False
):
  pars = ['--help']
  if as_status:
    pars = [
      '-i', 'batservice',
      '--icon', icon,
      '--ongoing', '--alert-once',
      '-t', 'Notify: %s' % (title),
      '-c', message,
      '--button1', 'encerrar', '--button1-action', 'termux-toast encerrar'
    ]
  else:
    pass

  try:
    if not as_toast:
      subprocess.run(
        [
          'termux-notification', *pars
        ],
        timeout = SUBPROCESS_TIMEOUT
      )
    if as_toast or as_error or as_fatal:
      subprocess.run(
        ['termux-toast', 'Notify: %s' % (message)],
        timeout = SUBPROCESS_TIMEOUT
      )
  except:
    tcount -= 1
    if tcount < 0:
      status_remove()
      raise RuntimeError('Termux:API commands are hanging frequently!')

  if as_fatal:
    status_remove()
    raise RuntimeError('FATAL: %s' % (message))


def send_message(message: str, title = 'mensagem do serviço', icon = 'battery_std'):
  pass


def send_status(
  btweaks: dict,
  remaining_time: Optional[int] = None
):
  message = '🔋 %d %% (%0.2f A) | 🌡 %0.1f °C' % (btweaks['percent'], btweaks['current'], btweaks['temp'])
  if btweaks['voltage'] is not None:
    message += ' | ⚡ %0.2f' % (btweaks['voltage'])
  termux_api_call(message, as_status = True)
  

def status_remove():
  try:
    subprocess.run(
      ['termux-notification-remove', 'batservice'],
      timeout = SUBPROCESS_TIMEOUT
    )
  except:
    pass