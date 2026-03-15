import os

import pytest

from parsons import Table

# Live test decorator
#
# Use the @pytest.mark.live decorator when authentication and/or
# network access is required. This will exclude them from our CI workflows,
# as authentication cannot be counted on within GitHub Actions.
#
# @pytest.mark.live
# def test_something_requiring_auth():
# service = SomeService()
# ...rest of test...


def pytest_configure(config):
    """Register `@pytest.mark.live` with pytest."""
    config.addinivalue_line(
        "markers", "live: mark test as requiring authentication and/or network access"
    )


def pytest_collection_modifyitems(config, items):
    """
    Add `@pytest.mark.skip` to tests with `@pytest.mark.live`, if appropriate.

    Tests will be marked to skip if the `LIVE_TEST` environment variable is not found.
    """
    if os.environ.get("LIVE_TEST", "").strip().upper() in ("1", "YES", "TRUE", "ON"):
        return
    skip_slow = pytest.mark.skip(reason="need LIVE_TEST environment variable to run")
    [item.add_marker(skip_slow) for item in items if "live" in item.keywords]


# Utility functions used in tests across multiple connectors


def validate_list(expected_keys: list, table: Table):
    """Test whether the columns of a Table match the provided list."""
    if set(expected_keys) != set(table.columns):
        raise KeyError("Not all expected keys found.")

    return True


def assert_matching_tables(table1, table2, ignore_headers=False):
    """
    Assert that two parsons Tables are the same.

    First checks that each has the same number of rows,
    then compares each row sequentially.
    """
    if ignore_headers:
        data1 = table1.data
        data2 = table2.data
    else:
        data1 = table1
        data2 = table2

    if isinstance(data1, Table) and isinstance(data2, Table):
        assert data1.num_rows == data2.num_rows

    for r1, r2 in zip(data1, data2, strict=False):
        # Cast both rows to lists, in case they are different types of collections.
        # Must call .items() on dicts to compare content of collections.
        r1_compare = r1.items() if isinstance(r1, dict) else r1
        r2_compare = r2.items() if isinstance(r2, dict) else r2

        assert list(r1_compare) == list(r2_compare)


@pytest.fixture
def sample_data() -> dict[str, list[dict[str, str | int]]]:
    """Provides sample dict containing two lists for use in tests."""
    return {
        "lst": [
            {"a": 1, "b": 2, "c": 3},
            {"a": 4, "b": 5, "c": 6},
            {"a": 7, "b": 8, "c": 9},
            {"a": 10, "b": 11, "c": 12},
            {"a": 13, "b": 14, "c": 15},
        ],
        "lst_dicts": [{"first": "Bob", "last": "Smith"}],
    }


@pytest.fixture
def tbl(sample_data) -> Table:
    """
    Provides a Table for use in tests.

    The table contains the data from the sample_data fixture.
    """
    return Table(sample_data["lst_dicts"])
