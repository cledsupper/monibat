import time
import math
from batttweaker import LeshtoBatt
from config.constants import DELAY_CHARGING, DELAY_DISCHARGING

batt = LeshtoBatt()

tm_saved = None

while True:
    tm = time.localtime()
    if tm_saved is None or tm.tm_mday != tm_saved.tm_mday:
        print('date: %d/%02d/%02d' % (tm.tm_year, tm.tm_mon, tm.tm_mday))
        tm_saved = tm

    current = batt.current_now()
    temp = batt.temp()
    current = current if current else math.nan
    temp = temp if temp else math.nan

    print('%2d:%02d { ' % (tm.tm_hour, tm.tm_min), end='')
    print('%d %%; ' % (batt.percent()), end='')
    print('%s; %0.2f A; ' % (batt.status(), current), end='')
    print('%0.1f °C }' % (temp))

    if batt.charging():
        time.sleep(DELAY_CHARGING)
    else:
        time.sleep(DELAY_CHARGING)
