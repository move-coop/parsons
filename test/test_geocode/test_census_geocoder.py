from unittest import mock

import petl
import pytest
import requests_mock

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
    cg.cg.onelineaddress.assert_called_with(address, returntype="geographies", timeout=None)
    assert geo == geographies_resp

    # Assert one line with locations parameter returns expected
    cg.cg.onelineaddress = mock.MagicMock(return_value=locations_resp)
    geo = cg.geocode_onelineaddress(address, return_type="locations")
    cg.cg.onelineaddress.assert_called_with(address, returntype="locations", timeout=None)
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
    cg.cg.address.assert_called_with(
        passed_address["address_line"],
        city=passed_address["city"],
        state=passed_address["state"],
        zipcode=None,
        returntype="geographies",
        timeout=None,
    )
    assert geo == geographies_resp

    # Assert one line with locations parameter returns expected
    cg.cg.address = mock.MagicMock(return_value=locations_resp)
    geo = cg.geocode_address(**passed_address, return_type="locations")
    cg.cg.address.assert_called_with(
        passed_address["address_line"],
        city=passed_address["city"],
        state=passed_address["state"],
        zipcode=None,
        returntype="locations",
        timeout=None,
    )
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


def test_timeout_forwarded_to_every_request():
    cg = CensusGeocoder(timeout=30)
    cg.cg = mock.MagicMock()
    cg.cg.onelineaddress = mock.MagicMock(return_value=geographies_resp)
    cg.cg.address = mock.MagicMock(return_value=geographies_resp)
    cg.cg.coordinates = mock.MagicMock(return_value={"States": [{}]})
    cg.cg.addressbatch = mock.MagicMock(return_value=batch_resp[:1])

    cg.geocode_onelineaddress("1600 Pennsylvania Avenue, Washington, DC")
    assert cg.cg.onelineaddress.call_args.kwargs["timeout"] == 30

    cg.geocode_address("1600 Pennsylvania Avenue", city="Washington", state="DC")
    assert cg.cg.address.call_args.kwargs["timeout"] == 30

    cg.get_coordinates_data("38.8884212", "-77.0441907")
    assert cg.cg.coordinates.call_args.kwargs["timeout"] == 30

    cg.geocode_address_batch(
        Table(
            [
                ["id", "street", "city", "state", "zip"],
                ["1", "908 N Washtenaw", "Chicago", "IL", "60622"],
            ]
        )
    )
    assert cg.cg.addressbatch.call_args.kwargs["timeout"] == 30


@pytest.mark.parametrize("status_code", [429, 500])
def test_geocode_address_batch_rejects_error_body(status_code):
    table = Table(
        [
            {
                "id": 1,
                "street": "1600 Pennsylvania Ave NW",
                "city": "Washington",
                "state": "DC",
                "zip": "20500",
            }
        ]
    )

    with requests_mock.Mocker() as m:
        m.post(
            requests_mock.ANY,
            status_code=status_code,
            text="<html>\n<body>Too Many Requests</body>\n</html>\n",
        )
        with pytest.raises(ValueError, match="response IDs do not match"):
            CensusGeocoder().geocode_address_batch(table)


@pytest.mark.parametrize("response_ids", [["1"], ["1", "1"], ["1", "2", "3"]])
def test_geocode_address_batch_rejects_incomplete_or_duplicate_results(cg, response_ids):
    table = Table(
        [
            ["id", "street", "city", "state", "zip"],
            [1, "1600 Pennsylvania Ave NW", "Washington", "DC", "20500"],
            [2, "908 N Washtenaw", "Chicago", "IL", "60622"],
        ]
    )
    cg.cg.addressbatch = mock.MagicMock(return_value=[{"id": id_} for id_ in response_ids])

    with pytest.raises(ValueError, match="response IDs do not match"):
        cg.geocode_address_batch(table)


def test_geocode_address_batch_accepts_reordered_unmatched_results():
    table = Table(
        [
            ["id", "street", "city", "state", "zip"],
            [1, "1600 Pennsylvania Ave NW", "Washington", "DC", "20500"],
            [None, "908 N Washtenaw", "Chicago", "IL", "60622"],
        ]
    )

    with requests_mock.Mocker() as m:
        m.post(requests_mock.ANY, text='"","908 N Washtenaw",No_Match\n1,address,No_Match\n')
        result = CensusGeocoder().geocode_address_batch(table)

    assert result["id"] == ["", "1"]
    assert result["match"] == [False, False]
