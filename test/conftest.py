import os
import warnings

import pytest
from _pytest.mark import MarkDecorator

from parsons import Table

# Live test decorator + pytest command-line flag
#
# Use the @pytest.mark.live decorator when authentication and/or
# network access is required. This will exclude them from our CI workflows,
# as authentication cannot be counted on within GitHub Actions.
#
# @pytest.mark.live
# def test_something_requiring_auth():
# service = SomeService()
# ...rest of test...


def mark_live_test(func) -> MarkDecorator:
    """Alias `@pytest.mark.live` as `@mark_live_test` with deprecation message."""
    warnings.warn(
        "Marking tests with @mark_live_test is deprecated, use @pytest.mark.live instead.",
        category=pytest.PytestDeprecationWarning,
        stacklevel=2,
    )
    return pytest.mark.live(func)


def pytest_addoption(parser) -> None:
    """Add pytest command-line flag `--live` to activate live tests"""
    parser.addoption(
        "--live",
        action="store_true",
        default=False,
        help="run tests requiring authentication and/or network access",
    )


def pytest_configure(config) -> None:
    """Register `@pytest.mark.live` with pytest."""
    config.addinivalue_line(
        "markers", "live: mark test as requiring authentication and/or network access"
    )


def pytest_collection_modifyitems(config, items) -> None:
    """
    Add `@pytest.mark.skip` to tests with `@pytest.mark.live`, if appropriate.

    Tests will be marked to skip if pytest is not run with `--live` and
    the `LIVE_TEST` environment variable is not found.
    """
    accepted_env_values = ("1", "YES", "TRUE", "ON")
    live_testing_environment = (
        os.environ.get("LIVE_TEST", "").strip().upper() in accepted_env_values
    )
    if config.getoption("--live") or live_testing_environment:
        return
    skip_slow = pytest.mark.skip(reason="need --live option to run")
    [item.add_marker(skip_slow) for item in items if "live" in item.keywords]


# Utility functions used in tests across multiple connectors


def validate_list(expected_keys: set | list, table: Table) -> bool:
    """Test whether the columns of a Table match those provided."""
    if set(expected_keys) != set(table.columns):
        raise KeyError("Not all expected keys found.")

    return True


def assert_matching_tables(
    table1: Table | dict, table2: Table | dict, ignore_headers: bool = False
) -> None:
    """
    Assert that two parsons Tables or dicts are the same.

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
