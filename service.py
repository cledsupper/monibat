#!/data/data/com.termux/files/usr/bin/python

# service.py - MoniBat Main Application Wrapper
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

import signal
import sys

from config.tweaker import logging, os, APP_PID, CACHE, CONFIG, FCACHE, FPID
import eventloop as main

if __name__ == '__main__':
    os.makedirs(CONFIG, exist_ok=True)
    os.makedirs(CACHE, exist_ok=True)
    with open(FPID, 'w') as file:
        file.write('%d\n' % (APP_PID))

    fcache = open(FCACHE, 'a')
    sys.o_stdout = sys.stdout
    sys.o_stderr = sys.stderr
    sys.stdout = fcache
    sys.stderr = fcache

    signal.signal(signal.SIGINT, main.handle_sigterm)
    signal.signal(signal.SIGTERM, main.handle_sigterm)

    ok = True
    while ok:
        try:
            main.iterate()
        except Exception:
            logging.exception('eventloop')
            break

        try:
            with open(FPID, 'r') as file:
                if int(file.read()) != APP_PID:
                    ok = not ok
        except FileNotFoundError:
            break

    if ok:
        try:
            os.remove(FPID)
        except FileNotFoundError:
            pass
        main.handle_sigterm(0, None)

    main.cleanup()

# by cleds.upper
