from os import path, remove
import logging.config
import json

from .Migrate import Migrate

# If applicable, delete the existing log file to generate a fresh log file during each execution
if path.isfile("logging/migration.log"):
    remove("logging/migration.log")

with open("logging/migration.json", 'r') as logging_configuration_file:
    config_dict = json.load(logging_configuration_file)

logging.config.dictConfig(config_dict)

# Log that the logger was configured
logger = logging.getLogger(__name__)
logger.info('Completed configuring logger()!')