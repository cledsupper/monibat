#!/data/data/com.termux/files/usr/bin/python
import logging
import signal
import sys

from config.tweaker import os, APP_PID, CACHE, CONFIG, FCACHE, FPID
import eventloop as main

if __name__ == '__main__':
  os.makedirs(CONFIG, exist_ok = True)
  os.makedirs(CACHE, exist_ok = True)
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