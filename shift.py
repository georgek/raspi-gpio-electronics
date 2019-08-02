#!/usr/bin/env python

"""This uses a shift register to make a binary counter.  Using an SN74HC595
and putting 8 bits on using SPI.

Chip layout:

     +-u-+
Q_B -|   |- V_{CC}
Q_C -|   |- Q_A
Q_D -|   |- SER
Q_E -|   |- ¬OE
Q_F -|   |- RCLK
Q_G -|   |- SRCLK
Q_H -|   |- ¬SRCLR
GND -|   |- Q_{H'}
     +---+

¬OE: Output Enable. Bring high to disable outputs Q_A-Q_H.
¬SRCLR: Shift Register Clear. Bring low to clear.
SER: Serial input.
SRCLK: Shift-Register Clock. On rising edge value of SER is shifted into
       shift-register.
RCLK: Storage-Register Clock. On rising edge shift-register stored in
      storage-register.
Q_A-Q_H: Storage-register outputs.

"""

import time
import random
import threading
import itertools

from idler import idler

try:
    import RPi.GPIO as gpio
except (ModuleNotFoundError, RuntimeError):
    pass

CLOCK_FREQ = 10000000           # 10 MHz
SLEEP = 1/CLOCK_FREQ/2

SER = 17
RCLK = 27
SRCLK = 22


def send_to_chip(n):
    """Send 8 bits to chip with SPI."""
    assert n < 256
    mask = 128

    gpio.output(RCLK, False)
    time.sleep(SLEEP)

    for _ in range(8):
        gpio.output(SER, n & mask)
        gpio.output(SRCLK, True)
        time.sleep(SLEEP)
        gpio.output(SRCLK, False)
        time.sleep(SLEEP)
        mask >>= 1

    gpio.output(RCLK, True)
    time.sleep(SLEEP)


def counter(finished):
    for n in itertools.cycle(range(255)):
        if finished.is_set():
            return
        send_to_chip(n)
        time.sleep(0.1)


def slider(finished):
    for n in itertools.cycle(range(8)):
        if finished.is_set():
            return
        send_to_chip(1 << n)
        time.sleep(0.1)


def rand(finished):
    while not finished.is_set():
        send_to_chip(random.randint(1, 255))
        time.sleep(0.1)


def main():
    gpio.setmode(gpio.BCM)

    gpio.setup(SER, gpio.OUT)
    gpio.setup(RCLK, gpio.OUT, initial=True)
    gpio.setup(SRCLK, gpio.OUT, initial=False)

    lights_finish = threading.Event()
    lights_thread = threading.Thread(target=counter, args=(lights_finish,))
    # lights_thread = threading.Thread(target=slider, args=(lights_finish,))
    # lights_thread = threading.Thread(target=rand, args=(lights_finish,))
    lights_thread.start()

    def cleanup():
        lights_finish.set()
        lights_thread.join()
        send_to_chip(0)
        gpio.cleanup()

    idler(cleanup_fun=cleanup)


if __name__ == '__main__':
    main()
