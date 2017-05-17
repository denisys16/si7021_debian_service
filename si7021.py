#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import threading
import smbus


try:
    import mlogger.mlogger as mlogger
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
    import mlogger.mlogger as mlogger

# Logger deafults
LOG_FILENAME = "/tmp/si7021.log"
LOG_LEVEL = mlogger.logging.WARNING  # Could be e.g. DEBUG, INFO, WARNING, ERROR or CRITICAL
mlogger.configure(LOG_FILENAME, LOG_LEVEL)


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

def get_time():
    return time.strftime("%d %b %Y %H:%M:%S", time.localtime())

def get_cpu_temperature():
    try:
        with open('/sys/devices/virtual/hwmon/hwmon1/temp1_input', 'rb') as stream:
            temp = stream.read().strip()
            mlogger.logger.info("CPU Temperature: " + temp + " °C")
            return temp
    except BaseException:
        mlogger.logger.error("Error read CPU temperature.")
        return "Error"

def get_cpu_frequency():
    try:
        with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq', 'rb') as stream:
            freq = int(stream.read().strip()) / 1000
            mlogger.logger.info("CPU Frequency: " + str(freq) + " MHz")
            return freq
    except BaseException:
        mlogger.logger.error("Error read CPU frequency.")
        return "Error"

def get_si7021_data():
    try:
        # Get I2C bus (Номер шины в разных МК может отличаться. В PI3 - 1)
        bus = smbus.SMBus(0)

        # SI7021 address, 0x40(64)
        # 0xF5(245) Select Relative Humidity NO HOLD master mode
        bus.write_byte(0x40, 0xF5)

        time.sleep(0.3)

        # SI7021 address, 0x40(64)
        # Read data back, 2 bytes, Humidity MSB first
        data0 = bus.read_byte(0x40)
        data1 = bus.read_byte(0x40)

        # Convert the data
        Humidity = ((data0 * 256 + data1) * 125 / 65536.0) - 6

        time.sleep(0.3)

        # SI7021 address, 0x40(64)
        #       0xF3(243)   Select temperature NO HOLD master mode
        bus.write_byte(0x40, 0xF3)

        time.sleep(0.3)

        # SI7021 address, 0x40(64)
        # Read data back, 2 bytes, Temperature MSB first
        data0 = bus.read_byte(0x40)
        data1 = bus.read_byte(0x40)

        # Convert the data
        cTemp = ((data0 * 256 + data1) * 175.72 / 65536.0) - 46.85

        mlogger.logger.info("Environment Temperature: " + ("%.2f" % cTemp) + " °C")
        mlogger.logger.info("Environment Humidity: " + ("%.2f" % Humidity) + " %")

        return cTemp, Humidity
    except BaseException:
        mlogger.logger.error("Error read SI7021 data.")
        return "Error", "Error"

mlogger.logger.info("Service si7021 has started.")

def main_loop():
    msg_time = ("state/opi/time", get_time(), 0, False)

    msg_cpu_temperature = ("state/opi/cpu_temperature", get_cpu_temperature(), 0, False)
    msg_cpu_frequency = ("state/opi/cpu_frequency", get_cpu_frequency(), 0, False)

    env_temperature, env_humidity = get_si7021_data()
    msg_env_temperature = ("state/opi/env_temperature", ("%.2f" %env_temperature), 0, False)
    msg_env_humidity = ("state/opi/env_humidity", ("%.2f" %env_humidity), 0, False)

    msgs = [msg_time, msg_cpu_temperature, msg_cpu_frequency, msg_env_temperature, msg_env_humidity]


    try:
        publish.multiple(msgs, hostname=MQTT_SERVER, port=MQTT_SERVER_PORT, client_id=MQTT_CLIENT_ID)
    except BaseException:
        mlogger.logger.warning("MQTT Publish error.")

    threading.Timer(MQTT_PUBLISH_PERIOD, main_loop).start()

if __name__ == "__main__":
    main_loop()


