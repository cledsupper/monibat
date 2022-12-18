#!/data/data/com.termux/files/usr/bin/python
import events

if __name__ == '__main__':
  while True:
    if not events.run():
      break

# by cleds.upper