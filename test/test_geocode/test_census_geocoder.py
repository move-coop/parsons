from unittest import mock

import petl
import pytest

from parsons import CensusGeocoder, Table
from parsons.geocode.census_geocoder import REQUIRED_BATCH_COLUMNS
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


def test_batch_accepts_extra_columns_and_drops_them(cg):
    """Extra columns are ignored, so callers need not cut their source table."""
    sent = []

    def capture(tbl, **kwargs):
        sent.append(tbl.columns)
        return batch_resp

    cg.cg.addressbatch = capture
    source = Table(
        [
            ["id", "street", "city", "state", "zip", "voterid", "notes"],
            ["1", "908 N Washtenaw", "Chicago", "IL", "60622", "V9", "keep me"],
        ]
    )

    cg.geocode_address_batch(source)

    assert sent == [REQUIRED_BATCH_COLUMNS]
    # the caller's table is untouched, so the join back to source rows survives
    assert source.columns == ["id", "street", "city", "state", "zip", "voterid", "notes"]


def test_batch_accepts_columns_in_any_order(cg):
    sent = []

    def capture(tbl, **kwargs):
        sent.append(tbl.columns)
        return batch_resp

    cg.cg.addressbatch = capture
    cg.geocode_address_batch(
        Table([["zip", "state", "city", "street", "id"], ["60622", "IL", "Chicago", "908 N", "1"]])
    )

    assert sent == [REQUIRED_BATCH_COLUMNS]


def test_batch_still_rejects_missing_columns(cg):
    cg.cg.addressbatch = mock.MagicMock(return_value=batch_resp)

    with pytest.raises(ValueError, match="missing required columns"):
        cg.geocode_address_batch(Table([["id", "street", "city"], ["1", "908 N", "Chicago"]]))

    cg.cg.addressbatch.assert_not_called()
