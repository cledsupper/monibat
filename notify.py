# notify.py - MoniBat Termux:API Interface
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
# -> events


import calendar
import logging
import subprocess
import time
from typing import Optional

from config.constants import APP_NAME, APP_PID, APP_PY, LEVEL, LEVEL_LOW, SUBPROCESS_TIMEOUT
from data.messages import *

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
    title=NOTIFY_BATTERY_STATUS_TITLE,
    perc=LEVEL_LOW,
    as_status=False,
    as_toast=False,
    as_error=False,
    as_fatal=False
):
    pars = ['--help']
    if as_status:
        if perc <= 0:
            perc = 0
        elif perc >= 100:
            perc = 100
        else:
            perc -= 1
        pars = [
            '-i', 'batservice',
            '--icon', icon,
            '--ongoing', '--alert-once',
            '-t', '%s: %s' % (APP_NAME, title),
            '-c', message,
            '--button1', NOTIFY_BATTERY_STATUS_BUTTON_RECALIBRATE, '--button1-action', 'python %s' % (
                APP_PY),
            '--button2', NOTIFY_BATTERY_STATUS_BUTTON_RESTART, '--button2-action', 'python %s %d' % (
                APP_PY, perc),
            '--button3', NOTIFY_BATTERY_STATUS_BUTTON_EXIT, '--button3-action', 'kill %d' % (
                APP_PID)

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
    except subprocess.SubprocessError as e:
        logging.debug(e)
        logging.debug(
            " :::===::: CHILD PROCESS' ERROR OUTPUT :::===:::")
        logging.debug(e.stderr.decode() if e.stderr else '')
        logging.debug(
            " :===: END OF CHILD PROCESS' ERROR OUTPUT :===:")

    if as_fatal:
        raise RuntimeError('FATAL: %s' % (message))


def send_message(message: str, title=NOTIFY_MESSAGE_TITLE, icon='battery_std'):
    termux_api_call(
        message,
        title=title,
        icon=icon
    )


display_percent = None

def send_status(
    btweaks: dict,
    remaining_time: Optional[time.struct_time] = None
):
    global status_shown
    global display_percent
    p = btweaks['percent']
    if display_percent is None or p < 5:
        display_percent = p
    else:
        dp = p - display_percent
        if dp < 0:
            display_percent -= 1
        elif dp > 0:
            display_percent += 1

    icon = 'battery_std'
    if btweaks['status'] == 'Charging':
        icon = 'battery_charging_full'
    elif btweaks['level'] == 'Low' or btweaks['level'] == 'Critical':
        icon = 'battery_alert'

    if btweaks['scale'] is None or btweaks['status'] == 'Charging':
        message = '%d %% (%0.2f A) | 🌡 %0.1f °C' % (
            display_percent, btweaks['current'], btweaks['temp'])
    else:
        message = '%d %% | 🌡 %0.1f °C' % (
            display_percent, btweaks['temp'])

    if btweaks['voltage'] is not None:
        message += ' | ⚡ %0.2f V' % (btweaks['voltage'])
    if btweaks['scale'] is not None:
        message += ' | 🩺 %0.2f' % (btweaks['scale'])

    title = LEVEL[btweaks['level']]
    if remaining_time:
        t = remaining_time
        st = calendar.timegm(t)
        if st >= 86400:
            title = NOTIFY_BATTERY_STATUS_REMAINING_DAYS % (
                t.tm_mday, t.tm_hour)
        elif st >= 3600:
            title = NOTIFY_BATTERY_STATUS_REMAINING_HOURS % (
                t.tm_hour, t.tm_min)
        elif st >= 60:
            title = NOTIFY_BATTERY_STATUS_REMAINING_MINS % (t.tm_min, t.tm_sec)

    termux_api_call(
        message,
        perc=btweaks['percent'],
        icon=icon,
        title=title,
        as_status=True
    )

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
