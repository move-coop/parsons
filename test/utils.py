from parsons.etl.table import Table
import os
import pytest

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


# Tests whether a table has the expected structure
def validate_list(expected_keys, table):

    if set(expected_keys) != set(table.columns):
        raise KeyError("Not all expected keys found.")

    return True


def assert_matching_tables(table1, table2, ignore_headers=False):
    if ignore_headers:
        data1 = table1.data
        data2 = table2.data
    else:
        data1 = table1
        data2 = table2

    if isinstance(data1, Table) and isinstance(data2, Table):
        assert data1.num_rows == data2.num_rows

    for r1, r2 in zip(data1, data2):
        # Cast both rows to lists, in case they are different types of collections. Must call
        # .items() on dicts to compare content of collections
        if isinstance(r1, dict):
            r1 = r1.items()
        if isinstance(r2, dict):
            r2 = r2.items()

        assert list(r1) == list(r2)
