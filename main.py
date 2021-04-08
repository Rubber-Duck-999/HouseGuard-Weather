#!/usr/bin/env python3

import time
import colorsys
import os
import sys
from bme280 import BME280
from subprocess import PIPE, Popen
import logging

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.info("Starting program")

# BME280 temperature/pressure/humidity sensor
bme280 = BME280()


# Get the temperature of the CPU for compensation
def get_cpu_temperature():
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE, universal_newlines=True)
    output, _error = process.communicate()
    return float(output[output.index('=') + 1:output.rindex("'")])


# Tuning factor for compensation. Decrease this number to adjust the
# temperature down, and increase to adjust up
factor = 2.25

cpu_temps = [get_cpu_temperature()] * 5

# The main loop
try:
    while True:
        # One mode for each variable
        # variable = "temperature"
        cpu_temp = get_cpu_temperature()
        # Smooth out with some averaging to decrease jitter
        cpu_temps = cpu_temps[1:] + [cpu_temp]
        avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
        raw_temp = bme280.get_temperature()
        data = raw_temp - ((avg_cpu_temp - raw_temp) / factor)
        logging.info("{:.2f}'C".format(data))
        time.sleep(5)

# Exit cleanly
except KeyboardInterrupt:
    sys.exit(0)