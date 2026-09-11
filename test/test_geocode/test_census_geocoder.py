from unittest import mock

import petl
import pytest
import requests

from parsons import CensusGeocoder, Table
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


def test_retry_recovers_from_transient_failure():
    cg = CensusGeocoder(retries=3)
    cg.cg = mock.MagicMock()
    cg.cg.onelineaddress = mock.MagicMock(
        side_effect=[
            requests.exceptions.ConnectionError("reset"),
            requests.exceptions.Timeout("slow"),
            geographies_resp,
        ]
    )

    with mock.patch("parsons.geocode.census_geocoder.time.sleep") as sleep:
        geo = cg.geocode_onelineaddress("1600 Pennsylvania Avenue, Washington, DC")

    assert geo == geographies_resp
    assert cg.cg.onelineaddress.call_count == 3
    # exponential backoff: 2 ** attempt
    assert [call.args[0] for call in sleep.call_args_list] == [1, 2]


def test_retry_reraises_once_exhausted():
    cg = CensusGeocoder(retries=2)
    cg.cg = mock.MagicMock()
    cg.cg.onelineaddress = mock.MagicMock(side_effect=requests.exceptions.ConnectionError("down"))

    with (
        mock.patch("parsons.geocode.census_geocoder.time.sleep"),
        pytest.raises(requests.exceptions.ConnectionError),
    ):
        cg.geocode_onelineaddress("1600 Pennsylvania Avenue, Washington, DC")

    assert cg.cg.onelineaddress.call_count == 3


def test_no_retry_by_default(cg):
    cg.cg = mock.MagicMock()
    cg.cg.onelineaddress = mock.MagicMock(side_effect=requests.exceptions.ConnectionError("down"))

    with (
        mock.patch("parsons.geocode.census_geocoder.time.sleep") as sleep,
        pytest.raises(requests.exceptions.ConnectionError),
    ):
        cg.geocode_onelineaddress("1600 Pennsylvania Avenue, Washington, DC")

    assert cg.cg.onelineaddress.call_count == 1
    sleep.assert_not_called()


def test_retry_applies_to_every_method():
    cg = CensusGeocoder(retries=1)
    cg.cg = mock.MagicMock()
    cg.cg.address = mock.MagicMock(
        side_effect=[requests.exceptions.ConnectionError("x"), geographies_resp]
    )
    cg.cg.coordinates = mock.MagicMock(
        side_effect=[requests.exceptions.ConnectionError("x"), {"States": [{}]}]
    )
    cg.cg.addressbatch = mock.MagicMock(
        side_effect=[requests.exceptions.ConnectionError("x"), batch_resp]
    )

    with mock.patch("parsons.geocode.census_geocoder.time.sleep"):
        cg.geocode_address("1600 Pennsylvania Avenue", city="Washington", state="DC")
        cg.get_coordinates_data("38.8884212", "-77.0441907")
        cg.geocode_address_batch(
            Table(
                [
                    ["id", "street", "city", "state", "zip"],
                    ["1", "908 N Washtenaw", "Chicago", "IL", "60622"],
                ]
            )
        )

    assert cg.cg.address.call_count == 2
    assert cg.cg.coordinates.call_count == 2
    assert cg.cg.addressbatch.call_count == 2


def test_negative_retries_rejected():
    with pytest.raises(ValueError, match="retries must be 0 or greater"):
        CensusGeocoder(retries=-1)
