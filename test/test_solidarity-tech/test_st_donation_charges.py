"""Tests for the Donation Charges methods of :class:`~parsons.solidarity_tech.SolidarityTech`."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from requests_mock import Mocker

    from parsons.solidarity_tech import SolidarityTech

ENDPOINT = "donation_charges"


class TestGetDonationCharges:
    # TODO(bmos): Implement this. Currently no example of what expected output will be.
    # @pytest.mark.vcr
    # def test_get_donation_charges_live(self, st: SolidarityTech) -> None:
    #    """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_donation_charges` returns both a Table of results and the associated metadata."""
    #    donation_charges, donation_charges_meta = st.get_donation_charges()
    #
    #    assert isinstance(donation_charges, Table)
    #    assert donation_charges.name == "Solidarity Tech Donation Charges"
    #    assert len(donation_charges) > 0
    #    assert isinstance(donation_charges[0], dict)
    #
    #    assert isinstance(donation_charges_meta, dict)
    #    assert donation_charges_meta["total_count"] > 0
    #    assert donation_charges_meta["limit"] == 20
    #    assert donation_charges_meta["offset"] == 0

    def test_get_donation_charges_minimal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_donation_charges` makes the appropriate calls."""
        endpoint_url = f"{st.api_url}{ENDPOINT}?_limit=20&_offset=0&_since=0"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _, _ = st.get_donation_charges()

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url

    def test_get_donation_charges_maximal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_donation_charges` makes the appropriate calls."""
        limit = 30
        offset = 5
        since = 1788075104
        endpoint_url = f"{st.api_url}{ENDPOINT}?_limit={limit}&_offset={offset}&_since={since}"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _, _ = st.get_donation_charges(limit=limit, offset=offset, since=since)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url


class TestGetDonationCharge:
    pass
    # TODO(bmos): Implement this. Currently no example of what expected output will be.
    # @pytest.mark.vcr
    # def test_get_donation_charge_live(self, st: SolidarityTech) -> None:
    #    """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_donation_charge` returns both a Table of results and the associated metadata."""
    #    resource_id = 478171
    #    donation_charge = st.get_donation_charge(resource_id=resource_id)
    #
    #    assert isinstance(donation_charge, dict)
    #    assert donation_charge["id"] == resource_id

    def test_get_donation_charge(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_donation_charge` makes the appropriate calls."""
        resource_id = 3598327
        endpoint_url = f"{st.api_url}{ENDPOINT}/{resource_id}"
        _ = requests_mock.get(endpoint_url, json={"data": {}, "meta": {}})

        _, _ = st.get_donation_charge(resource_id=resource_id)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url
