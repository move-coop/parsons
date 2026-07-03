import pytest

from parsons import Table
from test.conftest import assert_matching_tables
from test.test_google.googlecivic_responses import (
    elections_resp,
    polling_data,
    representatives_resp,
    voterinfo_resp,
)


def test_get_elections(googlecivic, requests_mock):
    requests_mock.get(googlecivic.uri + "elections", json=elections_resp)

    expected_tbl = Table(elections_resp["elections"])

    assert_matching_tables(googlecivic.get_elections(), expected_tbl)


def test_get_poll_location(googlecivic, requests_mock):
    requests_mock.get(googlecivic.uri + "voterinfo", json=voterinfo_resp)

    expected_tbl = Table(voterinfo_resp["pollingLocations"])

    tbl = googlecivic.get_polling_location(2000, "900 N Washtenaw, Chicago, IL 60622")

    assert_matching_tables(tbl, expected_tbl)


def test_get_poll_locations(googlecivic, requests_mock):
    requests_mock.get(googlecivic.uri + "voterinfo", json=voterinfo_resp)

    expected_tbl = Table(polling_data)

    address_tbl = Table(
        [
            ["address"],
            ["900 N Washtenaw, Chicago, IL 60622"],
            ["900 N Washtenaw, Chicago, IL 60622"],
        ]
    )

    tbl = googlecivic.get_polling_locations(2000, address_tbl)

    assert_matching_tables(tbl, expected_tbl)


def test_get_representative_info_by_address(googlecivic, requests_mock):
    requests_mock.get(googlecivic.uri + "representatives", json=representatives_resp)

    address = "1600 Amphitheatre Parkway, Mountain View, CA"  # replace with a valid address
    response = googlecivic.get_representative_info_by_address(address)

    assert isinstance(response, dict)
    assert "offices" in response
    assert "officials" in response
    assert "divisions" in response


def test_get_representative_info_by_address_invalid_input(googlecivic, requests_mock):
    requests_mock.get(googlecivic.uri + "representatives", json=representatives_resp)

    with pytest.raises(ValueError, match="address must be a string"):
        googlecivic.get_representative_info_by_address(123)

    with pytest.raises(ValueError, match="levels must be a list of strings"):
        googlecivic.get_representative_info_by_address(
            "1600 Amphitheatre Parkway, Mountain View, CA", levels="country"
        )

    with pytest.raises(ValueError, match="roles must be a list of strings"):
        googlecivic.get_representative_info_by_address(
            "1600 Amphitheatre Parkway, Mountain View, CA", roles="headOfGovernment"
        )


def test_get_representative_info_by_address_different_params(googlecivic, requests_mock):
    requests_mock.get(googlecivic.uri + "representatives", json=representatives_resp)

    address = "1600 Amphitheatre Parkway, Mountain View, CA"
    response = googlecivic.get_representative_info_by_address(
        address,
        include_offices=False,
        levels=["country"],
        roles=["headOfGovernment"],
    )

    assert isinstance(response, dict)
    assert "offices" in response
    assert "officials" in response
    assert "divisions" in response
