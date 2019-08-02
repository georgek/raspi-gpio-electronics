#!/usr/bin/env python

import math
import time
import threading

try:
    import RPi.GPIO as gpio
except (ModuleNotFoundError, RuntimeError):
    pass

from idler import idler

FREQUENCY = 100
PULSE_WIDTH = 0.5


def pulse(channel, lfo_generator, finished):
    while not finished.is_set():
        PERIOD = 1/FREQUENCY
        pulse_width = lfo_generator()
        gpio.output(channel, 1)
        time.sleep(PERIOD * pulse_width)
        gpio.output(channel, 0)
        time.sleep(PERIOD * (1-pulse_width))

    gpio.output(channel, 0)


def lfo_sine(frequency):
    period = 1/frequency

    def get_val():
        t = time.time() % period
        val = math.sin(t/period * math.pi*2)
        return val

    return get_val


def main():
    gpio.setmode(gpio.BCM)

    led = 4

    gpio.setup(led, gpio.OUT)

    lfo_generator = lfo_sine(0.5)

    def brightness():
        return abs(lfo_generator())

    pulse_finish = threading.Event()
    pulse_thread = threading.Thread(
        target=pulse,
        args=(led, brightness, pulse_finish))
    pulse_thread.start()

    def idler_info():
        return " ({:.3f})".format(brightness())

    def end_idle():
        pulse_finish.set()
        pulse_thread.join()
        gpio.cleanup()

    idler(idler_info, end_idle)


if __name__ == '__main__':
    main()
