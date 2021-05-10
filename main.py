#!/usr/bin/env python3
'''
Weather temperature script
'''

import time
import os
import logging
from subprocess import PIPE, Popen
from bme280 import BME280
import requests

logging.basicConfig(level=logging.INFO)
logging.info("Starting program")

class Temperature:
    '''Class for managing system and node temp'''
    SECONDS_PER_MINUTE = 60

    def __init__(self):
        '''Constructor'''
        logging.info('__init__()')
        # BME280 temperature/pressure/humidity sensor
        # Tuning factor for compensation. Decrease this number to adjust the
        # temperature down, and increase to adjust up
        self.factor     = 1
        self.bme280     = BME280()
        self.send_data  = False
        self.cpu_temp   = 0.0
        # Default of 10 minutes
        self.wait_time      = 10 * Temperature.SECONDS_PER_MINUTE
        self.server_address = ''
        self.temperature    = 0

    def get_env_var(self):
        '''Get config env var'''
        try:
            self.wait_time      = int(os.environ["weather_wait_time"])
            self.server_address = os.environ["server_address"]
            self.factor         = int(os.environ["temperature_factor"])
            self.send_data = True
        except KeyError:
            logging.error("Variables not set")
        self.wait_time = self.wait_time * Temperature.SECONDS_PER_MINUTE

    def get_cpu_temperature(self):
        '''Get the temperature of the CPU for compensation'''
        logging.info('get_cpu_temperature()')
        process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE, universal_newlines=True)
        output, _error = process.communicate()
        if process.returncode != 0:
            logging.error("Vcgencmd failed")
        else:
            self.cpu_temp = float(output[output.index('=') + 1:output.rindex("'")])

    def get_sensor_temperature(self):
        '''Grab the bme280 temp'''
        logging.info('get_sensor_temperature()')
        self.get_cpu_temperature()
        logging.info('CPU Temp: {}'.format(self.cpu_temp))
        raw_temp = self.bme280.get_temperature()
        logging.info('Raw Temp: {}'.format(raw_temp))
        self.temperature = raw_temp - ((self.cpu_temp - raw_temp) / self.factor)
        logging.info("Temperature: {:.2f}'C".format(self.temperature))

    def publish_data(self):
        '''Send data to server if asked'''
        if self.send_data:
            data = {
                'temperature': self.temperature
            }
            try:
                response = requests.post(self.server_address, data=data)
                if response.status_code == 200:
                    logging.info("Requests successful")
            except requests.ConnectionError as error:
                logging.error("Connection error: {}".format(error))
            except requests.Timeout as error:
                logging.error("Timeout on server: {}".format(error))

    def loop(self):
        '''Loop through sensor and publish'''
        self.get_env_var()
        while True:
            self.get_sensor_temperature()
            self.publish_data()
            time.sleep(self.wait_time)

temp = Temperature()
temp.loop()
