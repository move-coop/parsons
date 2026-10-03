"""Tests for the Organizations methods of :class:`~parsons.solidarity_tech.SolidarityTech`."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from parsons import Table

if TYPE_CHECKING:
    from requests_mock import Mocker

    from parsons.solidarity_tech import SolidarityTech

ENDPOINT = "organizations"


class TestGetOrganizations:
    @pytest.mark.vcr
    def test_get_organizations_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_organizations` returns both a Table of results and the associated metadata."""
        organizations, organizations_meta = st.get_organizations()

        assert isinstance(organizations, Table)
        assert organizations.name == "Solidarity Tech Organizations"
        assert len(organizations) > 0
        assert isinstance(organizations[0], dict)

        assert isinstance(organizations_meta, dict)
        assert organizations_meta["total_count"] > 0
        assert organizations_meta["limit"] == 20
        assert organizations_meta["offset"] == 0

    def test_get_organizations_minimal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_organizations` makes the appropriate calls."""
        endpoint_url = f"{st.api_url}{ENDPOINT}?_limit=20&_offset=0&_since=0"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _ = st.get_organizations()

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url

    def test_get_organizations_maximal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_organizations` makes the appropriate calls."""
        limit = 30
        offset = 5
        since = 1788075104
        endpoint_url = f"{st.api_url}{ENDPOINT}?_limit={limit}&_offset={offset}&_since={since}"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _ = st.get_organizations(
            limit=limit,
            offset=offset,
            since=since,
        )

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url


class TestGetOrganization:
    @pytest.mark.vcr
    def test_get_organization_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_organization` returns both a Table of results and the associated metadata."""
        resource_id = 187
        organization, organization_meta = st.get_organization(resource_id=resource_id)

        assert isinstance(organization, dict)
        assert organization["id"] == resource_id

        assert isinstance(organization_meta, dict)
        assert organization_meta["total_count"] > 0
        assert organization_meta["limit"] == 1
        assert organization_meta["offset"] == 0

    def test_get_organization(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_organization` makes the appropriate calls."""
        resource_id = 960
        endpoint_url = f"{st.api_url}{ENDPOINT}/{resource_id}"
        _ = requests_mock.get(endpoint_url, json={"data": {}, "meta": {}})

        _, _ = st.get_organization(resource_id=resource_id)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url
