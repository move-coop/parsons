# -*- coding: utf-8 -*-

# This file is part of censusgeocode.
# https://github.com/fitnr/censusgeocode

# Licensed under the General Public License (version 3)
# http://opensource.org/licenses/LGPL-3.0
# Copyright (c) 2015-9, Neil Freeman <contact@fakeisthenewreal.org>

import warnings
from .censusgeocode import CensusGeocode

__version__ = '0.5.2'

warnings.warn(
    (
        "CensusGeocoder will be removed in parsons version 6.0.0, "
        "unless the censusgeocode package is updated to allow newer versions of urllib3."
    ),
    category=FutureWarning,
    stacklevel=2,
)

cg = CensusGeocode()

coordinates = cg.coordinates
address = cg.address
onelineaddress = cg.onelineaddress
addressbatch = cg.addressbatch
