import os

import pytest

from parsons import Table

"""
Use this as a marker before any tests that hit live services. That way they'll only run
if you set the "LIVE_TEST" env var.
Example usage:

@mark_live_test
def test_something():
    service = SomeService()
    ...
"""
mark_live_test = pytest.mark.skipif(
    not os.environ.get("LIVE_TEST"), reason="Skipping because not running live test"
)



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
