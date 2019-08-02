#!/usr/bin/env python

import sys
import time


def idler(info_fun=None, cleanup_fun=None):
    chars = ['/', '-', '\\', '|']
    n = 0
    try:
        while True:
            n = (n+1) % 4
            if info_fun:
                info = info_fun()
            else:
                info = ""
            sys.stdout.write("\r{}{}".format(chars[n], info))
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\r")
        if cleanup_fun:
            cleanup_fun()
