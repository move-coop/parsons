# ### METADATA

# Connectors:
# Description:

# ### CONFIGURATION

# Set the configuration variables below or set environmental variables of the same name and leave
# these with empty strings.  We recommend using environmental variables if possible.

# //To Script Writer// : add the environmental variable name but not the value
# //To Script Writer// : separate environmental variables by connector

config_vars = {
    # Connector 1:
    "EXAMPLE_VARIABLE_NAME": "",
    # Connector 2:
    "ANOTHER_EXAMPLE_VARIABLE_NAME": ""
}


# ### CODE

# //To Script Writer//: import any other packages your script uses
import os  # noqa: E402

# //To Script Writer//: import any connectors your script uses
# from parsons import utilities, logger

# Setup

# if variables specified above, sets themas environmental variables
for name, value in config_vars.items():
    if value.strip() != "":
        os.environ[name] = value

# //To Script Writer// : instantiate connectors here, eg: rs = Redshift().

# Code
