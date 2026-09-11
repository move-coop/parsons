import threading
from unittest import mock

import petl
import pytest

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


def _batch_table(n):
    return Table(
        [["id", "street", "city", "state", "zip"]]
        + [[str(i), f"{i} Main St", "Chicago", "IL", "60622"] for i in range(1, n + 1)]
    )


def test_default_is_sequential(cg):
    assert cg.workers == 1
    threads = set()

    def record(tbl, **kwargs):
        threads.add(threading.current_thread().name)
        return batch_resp

    cg.cg.addressbatch = record
    with mock.patch.object(census_geocoder, "BATCH_SIZE", 2):
        cg.geocode_address_batch(_batch_table(6))

    assert threads == {threading.current_thread().name}


def test_workers_run_chunks_in_parallel():
    cg = CensusGeocoder(workers=3)
    cg.cg = mock.MagicMock()
    # every chunk must reach the barrier before any is released, so this only
    # completes if the three chunks are genuinely in flight at the same time
    barrier = threading.Barrier(3, timeout=10)
    threads = set()

    def blocking(tbl, **kwargs):
        threads.add(threading.current_thread().name)
        barrier.wait()
        return batch_resp

    cg.cg.addressbatch = blocking
    with mock.patch.object(census_geocoder, "BATCH_SIZE", 2):
        cg.geocode_address_batch(_batch_table(6))

    assert threading.current_thread().name not in threads
    assert len(threads) == 3


def test_worker_output_preserves_input_order():
    cg = CensusGeocoder(workers=3)
    cg.cg = mock.MagicMock()

    def per_chunk(tbl, **kwargs):
        # echo the chunk's own ids back so ordering is observable
        return [{"id": row["id"], "match": True} for row in tbl]

    cg.cg.addressbatch = per_chunk
    with mock.patch.object(census_geocoder, "BATCH_SIZE", 2):
        geo = cg.geocode_address_batch(_batch_table(6))

    assert [row["id"] for row in geo] == ["1", "2", "3", "4", "5", "6"]


@pytest.mark.parametrize("count", [0, -1])
def test_non_positive_workers_rejected(count):
    with pytest.raises(ValueError, match="workers must be 1 or greater"):
        CensusGeocoder(workers=count)
