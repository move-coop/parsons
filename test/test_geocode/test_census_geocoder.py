from unittest import mock

import petl
import pytest
import requests

from parsons import CensusGeocoder, Table
from parsons.geocode import census_geocoder
from test.conftest import assert_matching_tables

from .test_responses import batch_resp, coord_resp, geographies_resp, locations_resp


@pytest.fixture
def cg():
    """Provides a fresh CensusGeocoder instance for each test."""
    return CensusGeocoder()


def test_geocode_onelineaddress(cg):
    cg.cg = mock.MagicMock()
    address = "1600 Pennsylvania Avenue, Washington, DC"

    # Assert one line with geographies parameter returns expected
    cg.cg.onelineaddress = mock.MagicMock(return_value=geographies_resp)
    geo = cg.geocode_onelineaddress(address, return_type="geographies")
    cg.cg.onelineaddress.assert_called_with(address, returntype="geographies")
    assert geo == geographies_resp

    # Assert one line with locations parameter returns expected
    cg.cg.onelineaddress = mock.MagicMock(return_value=locations_resp)
    geo = cg.geocode_onelineaddress(address, return_type="locations")
    cg.cg.onelineaddress.assert_called_with(address, returntype="locations")
    assert geo == locations_resp


def test_geocode_address(cg):
    cg.cg = mock.MagicMock()
    passed_address = {
        "address_line": "1600 Pennsylvania Avenue",
        "city": "Washington",
        "state": "DC",
    }

    # Assert one line with geographies parameter returns expected
    cg.cg.address = mock.MagicMock(return_value=geographies_resp)
    geo = cg.geocode_address(**passed_address, return_type="geographies")
    assert geo == geographies_resp

    # Assert one line with locations parameter returns expected
    cg.cg.address = mock.MagicMock(return_value=locations_resp)
    geo = cg.geocode_address(**passed_address, return_type="locations")
    assert geo == locations_resp


def test_geocode_address_batch(cg):
    batch = [
        ["id", "street", "city", "state", "zip"],
        ["1", "908 N Washtenaw", "Chicago", "IL", "60622"],
        ["2", "1405 Wilshire Blvd", "Austin", "TX", "78722"],
        ["3", "908 N Washtenaw", "Chicago", "IL", "60622"],
        ["4", "1405 Wilshire Blvd", "Austin", "TX", "78722"],
        ["5", "908 N Washtenaw", "Chicago", "IL", "60622"],
    ]

    tbl = Table(batch)

    cg.cg.addressbatch = mock.MagicMock(return_value=batch_resp)
    geo = cg.geocode_address_batch(tbl)
    assert_matching_tables(geo, Table(petl.fromdicts(batch_resp)))


@pytest.mark.vcr
def test_coordinates(cg):
    # Assert coordinates data returns expected response.
    cg.cg.address = mock.MagicMock(return_value=coord_resp)
    geo = cg.get_coordinates_data("38.8884212", "-77.0441907")
    assert geo == coord_resp


BATCH_HEADER = ["id", "street", "city", "state", "zip"]


def _batch_table(n):
    return Table(
        [BATCH_HEADER]
        + [[str(i), f"{i} Main St", "Chicago", "IL", "60622"] for i in range(1, n + 1)]
    )


def test_batch_raises_and_loses_work_by_default(cg):
    calls = {"n": 0}

    def flaky(tbl, **kwargs):
        calls["n"] += 1
        if calls["n"] == 3:
            raise requests.exceptions.ConnectionError("chunk 3 died")
        return batch_resp

    cg.cg.addressbatch = flaky

    with (
        mock.patch.object(census_geocoder, "BATCH_SIZE", 2),
        pytest.raises(requests.exceptions.ConnectionError),
    ):
        cg.geocode_address_batch(_batch_table(6))

    assert calls["n"] == 3


def test_batch_returns_completed_chunks_when_opted_in(cg):
    calls = {"n": 0}

    def flaky(tbl, **kwargs):
        calls["n"] += 1
        if calls["n"] == 3:
            raise requests.exceptions.ConnectionError("chunk 3 died")
        return batch_resp

    cg.cg.addressbatch = flaky

    with mock.patch.object(census_geocoder, "BATCH_SIZE", 2):
        geo = cg.geocode_address_batch(_batch_table(6), return_partial_on_error=True)

    # two chunks completed before the failure, each returning the full batch fixture
    assert geo.num_rows == 2 * len(batch_resp)
    assert calls["n"] == 3


def test_batch_partial_covers_non_request_errors(cg):
    # A 5xx surfaces from censusgeocode as ValueError, not RequestException.
    cg.cg.addressbatch = mock.MagicMock(
        side_effect=[batch_resp, ValueError("Unable to parse response from Census")]
    )

    with mock.patch.object(census_geocoder, "BATCH_SIZE", 2):
        geo = cg.geocode_address_batch(_batch_table(4), return_partial_on_error=True)

    assert geo.num_rows == len(batch_resp)
