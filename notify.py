# notify.py - MoniBat Termux:API Interface
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
# -> events.py


import subprocess
from typing import Optional

from config.constants import APP_NAME, APP_PID, APP_PY, SUBPROCESS_TIMEOUT

subprocess.run(
    ['termux-toast', '-h'],
    capture_output=True,
    check=True,
    timeout=SUBPROCESS_TIMEOUT
)

subprocess.run(
    ['termux-notification', '-h'],
    capture_output=True,
    check=True,
    timeout=SUBPROCESS_TIMEOUT
)

status_shown = False


def termux_api_call(
    message: str,
    icon='battery_std',
    title='estado da bateria',
    as_status=False,
    as_toast=False,
    as_error=False,
    as_fatal=False
):
    pars = ['--help']
    if as_status:
        pars = [
            '-i', 'batservice',
            '--icon', icon,
            '--ongoing', '--alert-once',
            '-t', '%s: %s' % (APP_NAME, title),
            '-c', message,
            '--button1', 'reiniciar', '--button1-action', 'python %s' % (
                APP_PY),
            '--button2', 'encerrar', '--button2-action', 'kill %d' % (APP_PID)
        ]
    else:
        pars = [
            '--icon', icon,
            '-t', '%s: %s' % (APP_NAME, title),
            '-c', message
        ]

    try:
        if not as_toast:
            subprocess.run(
                [
                    'termux-notification', *pars
                ],
                timeout=SUBPROCESS_TIMEOUT
            )
        if as_toast or as_error or as_fatal:
            subprocess.run(
                ['termux-toast', '-g', 'top', '%s: %s' % (APP_NAME, message)],
                timeout=SUBPROCESS_TIMEOUT
            )
    except:
        pass
    if as_fatal:
        raise RuntimeError('FATAL: %s' % (message))


def send_message(message: str, title='mensagem do serviço', icon='battery_std'):
    termux_api_call(
        message,
        title=title,
        icon=icon
    )


def send_status(
    btweaks: dict,
    remaining_time: Optional[int] = None
):
    global status_shown
    message = '🔋 %d %% (%0.2f A) | 🌡 %0.1f °C' % (
        btweaks['percent'], btweaks['current'], btweaks['temp'])
    if btweaks['voltage'] is not None:
        message += ' | ⚡ %0.2f V' % (btweaks['voltage'])
    if btweaks['energy'] is not None:
        message += ' | %0.2f Ah' % (btweaks['energy'])
    termux_api_call(message, as_status=True)
    if not status_shown:
        status_shown = True


def send_toast(message: str):
    termux_api_call(message, as_toast=True)


def status_remove():
    try:
        subprocess.run(
            ['termux-notification-remove', 'batservice'],
            timeout=SUBPROCESS_TIMEOUT
        )
    except:
        pass
