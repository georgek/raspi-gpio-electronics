#!/usr/bin/env python

import sys
import time

import RPi.GPIO as gpio

gpio.setmode(gpio.BCM)

led = 4
switch = 17

gpio.setup(led, gpio.OUT)
gpio.setup(switch, gpio.IN)

state = 0
gpio.output(led, state)


def toggle(channel):
    global state
    state = not state
    gpio.output(led, state)


gpio.add_event_detect(switch, gpio.FALLING, callback=toggle)

chars = ['/', '-', '\\', '|']
n = 0
try:
    while True:
        n = (n+1) % 4
        sys.stdout.write("\r{}".format(chars[n]))
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    gpio.cleanup()
    sys.stdout.write("\r")
