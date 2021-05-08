#!/usr/bin/env python3
'''
Weather temperature script
'''

import time
import os
import logging
from subprocess import PIPE, Popen
from bme280 import BME280

logging.basicConfig(level=logging.INFO)
logging.info("Starting program")

class Temperature:
    '''Class for managing system and node temp'''

    def __init__(self):
        '''Constructor'''
        logging.info('__init__()')
        # BME280 temperature/pressure/humidity sensor
        # Tuning factor for compensation. Decrease this number to adjust the
        # temperature down, and increase to adjust up
        self.factor = 1
        self.bme280 = BME280()
        self.raw_temp = 0.0

    def get_name(self):
        '''Check OS name'''
        logging.info('get_name()')
        if 'pi' in os.uname().nodename:
            logging.info("Device is a PI")
            self.name = 'pi'
        else:
            self.name = 'test'

    def get_cpu_temperature(self):
        '''Get the temperature of the CPU for compensation'''
        logging.info('get_cpu_temperature()')
        self.get_name()
        if self.name == 'pi':
            process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE, universal_newlines=True)
            output, _error = process.communicate()
            cpu_temp = float(output[output.index('=') + 1:output.rindex("'")])
        else:
            cpu_temp = 60
        logging.info('CPU Temp: {}'.format(cpu_temp))
        return cpu_temp

    def get_start_temperature(self):
        '''Get list'''
        self.cpu_temps = [self.get_cpu_temperature()] * 5

    def get_sensor_temperature(self):
        '''Grab the bme280 temp'''
        logging.info('get_sensor_temperature()')
        cpu_temp = self.get_cpu_temperature()
        # Smooth out with some averaging to decrease jitter
        self.cpu_temps = self.cpu_temps[1:] + [cpu_temp]
        logging.info('CPUs Temp: {}'.format(self.cpu_temps))
        avg_cpu_temp = sum(self.cpu_temps) / float(len(self.cpu_temps))
        logging.info('Average Temp: {}'.format(avg_cpu_temp))
        raw_temp = self.bme280.get_temperature()
        logging.info('Raw Temp: {}'.format(raw_temp))
        data = raw_temp - ((avg_cpu_temp - raw_temp) / self.factor)
        logging.info("Temperature: {:.2f}'C".format(data))

temp = Temperature()
temp.get_start_temperature()
while True:
    temp.get_sensor_temperature()
    time.sleep(5)