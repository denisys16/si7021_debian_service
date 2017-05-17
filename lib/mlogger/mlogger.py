#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logging.handlers
import sys
import time

# Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
# Give the logger a unique name (good practice)
logger = logging.getLogger(__name__)

# Make a class we can use to capture stdout and sterr in the log
class MLogger(object):
    def __init__(self, logger, level):
        """Needs a logger and a logger level."""
        self.logger = logger
        self.level = level

    def write(self, message):
        # Only log if there is a message (not just a new line)
        if message.rstrip() != "":
            self.logger.log(self.level, message.rstrip())


def configure(filename, level): # level could be e.g. logging.DEBUG, INFO, WARNING, ERROR or CRITICAL
    # Set the log level to LOG_LEVEL
    logger.setLevel(level)
    # Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
    handler = logging.handlers.TimedRotatingFileHandler(filename, when="midnight", backupCount=3)
    # Format each log message like this
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    # Attach the formatter to the handler
    handler.setFormatter(formatter)
    # Attach the handler to the logger
    logger.addHandler(handler)

    # Replace stdout with logging to file at INFO level
    sys.stdout = MLogger(logger, logging.INFO)
    # Replace stderr with logging to file at ERROR level
    sys.stderr = MLogger(logger, logging.ERROR)

if __name__ == "__main__":
    configure("/tmp/mlogger.log", logging.INFO)
    logger.info("This is mlogger test message.")



