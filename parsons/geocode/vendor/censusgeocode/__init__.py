# -*- coding: utf-8 -*-

# This file is part of censusgeocode.
# https://github.com/fitnr/censusgeocode

# Licensed under the General Public License (version 3)
# http://opensource.org/licenses/LGPL-3.0
# Copyright (c) 2015-9, Neil Freeman <contact@fakeisthenewreal.org>

from .censusgeocode import CensusGeocode

__version__ = '0.5.2'

cg = CensusGeocode()

coordinates = cg.coordinates
address = cg.address
onelineaddress = cg.onelineaddress
addressbatch = cg.addressbatch
