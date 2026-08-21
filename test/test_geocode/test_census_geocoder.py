"""Tests for the CensusGeocoder connector.

CensusGeocoder wraps a third-party ``censusgeocode.CensusGeocode`` client, so that
client is the boundary we mock (see the ``geocoder`` fixture in conftest.py) while
the connector's own methods run for real. Canned client responses live in ``data/``.

The pre-migration suite mocked the same client correctly, but the whole class was
marked ``@pytest.mark.live`` — so none of it ran in CI (0% mutation, 34% line). These
tests drop that marker so the mocked behaviour is actually exercised.
"""

import logging

import petl
import pytest

from parsons import Table
from test.conftest import assert_matching_tables


def test_geocode_onelineaddress(geocoder, load):
    address = "1600 Pennsylvania Avenue, Washington, DC"

    geographies = load("geographies_resp")
    geocoder.cg.onelineaddress.return_value = geographies
    assert geocoder.geocode_onelineaddress(address, return_type="geographies") == geographies
    geocoder.cg.onelineaddress.assert_called_with(address, returntype="geographies")

    locations = load("locations_resp")
    geocoder.cg.onelineaddress.return_value = locations
    assert geocoder.geocode_onelineaddress(address, return_type="locations") == locations
    geocoder.cg.onelineaddress.assert_called_with(address, returntype="locations")


def test_geocode_onelineaddress_logs_success(geocoder, load, caplog):
    geocoder.cg.onelineaddress.return_value = load("geographies_resp")

    with caplog.at_level(logging.INFO):
        geocoder.geocode_onelineaddress("1600 Pennsylvania Avenue")

    assert "Record geocoded." in caplog.text


def test_geocode_onelineaddress_logs_no_match(geocoder, caplog):
    # An address the service cannot geocode comes back as an empty list.
    geocoder.cg.onelineaddress.return_value = []

    with caplog.at_level(logging.INFO):
        result = geocoder.geocode_onelineaddress("nowhere")

    assert result == []
    assert "Unable to geocode record." in caplog.text


def test_geocode_address(geocoder, load):
    passed_address = {
        "address_line": "1600 Pennsylvania Avenue",
        "city": "Washington",
        "state": "DC",
    }

    geographies = load("geographies_resp")
    geocoder.cg.address.return_value = geographies
    assert geocoder.geocode_address(**passed_address, return_type="geographies") == geographies
    # NOTE: geocode_address does not forward return_type to the client (unlike
    # geocode_onelineaddress) — a latent source bug. Assert the call as it is today.
    geocoder.cg.address.assert_called_with(
        "1600 Pennsylvania Avenue", city="Washington", state="DC", zipcode=None
    )

    locations = load("locations_resp")
    geocoder.cg.address.return_value = locations
    assert geocoder.geocode_address(**passed_address, return_type="locations") == locations


def test_geocode_address_batch(geocoder, load, caplog):
    batch_resp = load("batch_resp")
    geocoder.cg.addressbatch.return_value = batch_resp

    tbl = Table(
        [
            ["id", "street", "city", "state", "zip"],
            ["1", "908 N Washtenaw", "Chicago", "IL", "60622"],
            ["2", "1405 Wilshire Blvd", "Austin", "TX", "78722"],
        ]
    )
    with caplog.at_level(logging.INFO):
        geo = geocoder.geocode_address_batch(tbl)

    assert geo.num_rows == len(batch_resp)
    assert_matching_tables(geo, Table(petl.fromdicts(batch_resp)))
    geocoder.cg.addressbatch.assert_called_once()
    assert "2 of 2 records processed." in caplog.text


def test_geocode_address_batch_rejects_wrong_columns(geocoder):
    tbl = Table([["id", "address"], ["1", "908 N Washtenaw"]])

    with pytest.raises(ValueError, match="Table must ONLY include"):
        geocoder.geocode_address_batch(tbl)

    geocoder.cg.addressbatch.assert_not_called()


def test_get_coordinates_data(geocoder, load, caplog):
    coord_resp = load("coord_resp")
    geocoder.cg.coordinates.return_value = coord_resp

    with caplog.at_level(logging.INFO):
        geo = geocoder.get_coordinates_data("38.8884212", "-77.0441907")

    assert geo == coord_resp
    # latitude is y, longitude is x.
    geocoder.cg.coordinates.assert_called_with(x="-77.0441907", y="38.8884212")
    assert "Coordinate processed." in caplog.text


def test_get_coordinates_data_not_found(geocoder, caplog):
    geocoder.cg.coordinates.return_value = {"States": []}

    with caplog.at_level(logging.INFO):
        geo = geocoder.get_coordinates_data("0", "0")

    assert geo == {"States": []}
    assert "Coordinate not found." in caplog.text
