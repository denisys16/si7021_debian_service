#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logging.handlers
import argparse
import sys
import time
import threading

try:
    import paho.mqtt.publish as publish
except ImportError:
    # This part is only required to run the example from within the examples
    # directory when the module itself is not installed.
    #
    # If you have the module installed, just use "import paho.mqtt.publish"
    import os
    import inspect
    cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"./lib")))
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)
    import paho.mqtt.publish as publish

MQTT_SERVER="192.168.1.108"
MQTT_SERVER_PORT=1883
MQTT_PUBLISH_PERIOD=5
MQTT_CLIENT_ID="opimonitormqtt002"

# Deafults
LOG_FILENAME = "/tmp/si7021.log"
LOG_LEVEL = logging.INFO  # Could be e.g. DEBUG, INFO, WARNING, ERROR or CRITICAL

# Define and parse command line arguments
parser = argparse.ArgumentParser(description="Si7021 service")
parser.add_argument("-l", "--log", help="file to write log to (default '" + LOG_FILENAME + "')")

# If the log file is specified on the command line then override the default
args = parser.parse_args()
if args.log:
    LOG_FILENAME = args.log

# Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
# Give the logger a unique name (good practice)
logger = logging.getLogger(__name__)
# Set the log level to LOG_LEVEL
logger.setLevel(LOG_LEVEL)
# Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
# Format each log message like this
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
# Attach the formatter to the handler
handler.setFormatter(formatter)
# Attach the handler to the logger
logger.addHandler(handler)

# Make a class we can use to capture stdout and sterr in the log
class MyLogger(object):
    def __init__(self, logger, level):
        """Needs a logger and a logger level."""
        self.logger = logger
        self.level = level

    def write(self, message):
        # Only log if there is a message (not just a new line)
        if message.rstrip() != "":
            self.logger.log(self.level, message.rstrip())

# Replace stdout with logging to file at INFO level
sys.stdout = MyLogger(logger, logging.INFO)
# Replace stderr with logging to file at ERROR level
sys.stderr = MyLogger(logger, logging.ERROR)

def get_time():
    return time.strftime("%d %b %Y %H:%M:%S", time.localtime())

def get_cpu_temperature():
    try:
        with open('/sys/devices/virtual/hwmon/hwmon1/temp1_input', 'rb') as stream:
            temp = stream.read().strip()
            logger.info(get_time() + " CPU Temperature: " + temp + " °C")
            return temp
    except BaseException:
        logger.warning(get_time() + " Error read CPU temperature.")
        return "Error"

def get_cpu_frequency():
    try:
        with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq', 'rb') as stream:
            freq = int(stream.read().strip()) / 1000
            logger.info(get_time() + " CPU Frequency: " + freq + " MHz")
            return freq
    except BaseException:
        logger.warning(get_time() + " Error read CPU frequency.")
        return "Error"

logger.info("Service si7021 has started " + get_time())

def main_loop():
    cur_time = get_time()
    cur_temperature = get_cpu_temperature()
    cur_freq = get_cpu_frequency()

    msg_time = ("state/opi/time", cur_time, 0, False)
    msg_temperature = ("state/opi/temperature", cur_temperature, 0, False)
    msg_freq = ("state/opi/freq", cur_freq, 0, False)
    msgs = [msg_time, msg_temperature, msg_freq]
    try:
        publish.multiple(msgs, hostname=MQTT_SERVER, port=MQTT_SERVER_PORT, client_id=MQTT_CLIENT_ID)
    except BaseException:
        logger.warning(get_time() + " MQTT Publish error.")

    threading.Timer(MQTT_PUBLISH_PERIOD, main_loop).start()

if __name__ == "__main__":
    main_loop()


