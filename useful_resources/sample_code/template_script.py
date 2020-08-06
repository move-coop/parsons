### METADATA

# Connectors: 
# Description:

### CONFIGURATION

# Set the configuration variables below or set environmental variables of the same name and leave these
# with empty strings.  We recommend using environmental variables if possible.

# //To Script Writer// : add the environmental variable name but not the value
# //To Script Writer// : separate environmental variables by connector

config_vars = {
    # Connector 1:
    "EXAMPLE_VARIABLE_NAME": "",
    # Connector 2:
    "ANOTHER_EXAMPLE_VARIABLE_NAME": ""
}


### CODE

import os, logging                 # //To Script Writer//: import any other packages your script uses
from parsons import utilities      # //To Script Writer//: import any connectors your script uses

# Setup

for name, value in config_vars.items():    # if variables specified above, sets them as environmental variables
    if value.strip() != "":
        os.environ[name] = value

# //To Script Writer// : instantiate connectors here, eg: rs = Redshift().

# Logging

logger = logging.getLogger(__name__)
_handler = logging.StreamHandler()
_formatter = logging.Formatter('%(levelname)s %(message)s')
_handler.setFormatter(_formatter)
logger.addHandler(_handler)
logger.setLevel('INFO')

# Code

