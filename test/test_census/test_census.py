import pytest

from parsons import Census, Table

from .conftest import MOCK_API_KEY


@pytest.mark.live
def test_get_census_live_test():
    census = Census()
    year = "2019"
    dataset_acronym = "/acs/acs1"
    variables = "NAME,B01001_001E"
    location = "for=state:*"
    table = census.get_census(year, dataset_acronym, variables, location)
    assert len(table) == 52
    assert table[0]["NAME"] == "Illinois"
    assert isinstance(table, Table)


def test_get_census_mock_test(census, requests_mock):
    year = "2019"
    dataset_acronym = "/acs/acs1"
    variables = "NAME,B01001_001E"
    location = "us:1"

    # This must match what get_census() will call under the hood
    expected_url = (
        "https://api.census.gov/data/2019/acs/acs1"
        f"?get=NAME,B01001_001E&for=us:1&key={MOCK_API_KEY}"
    )

    # Mock the actual HTTP response
    requests_mock.get(
        expected_url,
        json=[["NAME", "B01001_001E", "us"], ["United States", "328239523", "1"]],
    )

    table = census.get_census(year, dataset_acronym, variables, location)

    assert table[0]["B01001_001E"] == "328239523"
    assert table[0]["NAME"] == "United States"
