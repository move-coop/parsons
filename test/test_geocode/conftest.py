import json

import pytest

from parsons import CensusGeocoder


@pytest.fixture
def geocoder(mocker):
    """A CensusGeocoder with its third-party ``censusgeocode`` client mocked.

    The connector wraps a ``censusgeocode.CensusGeocode`` client (``self.cg``); that
    client is the external boundary, so we patch it at its import site and let the
    connector's own methods run against the mock. Program ``geocoder.cg.<method>``
    per test.
    """
    mocker.patch("parsons.geocode.census_geocoder.censusgeocode.CensusGeocode")
    return CensusGeocoder()


@pytest.fixture
def load(shared_datadir):
    """Load a canned censusgeocode response from the ``data/`` directory."""

    def _load(name: str):
        return json.loads((shared_datadir / f"{name}.json").read_text())

    return _load
