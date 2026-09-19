"""Tests for the Pages methods of :class:`~parsons.solidarity_tech.SolidarityTech`."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from parsons import Table

if TYPE_CHECKING:
    from requests_mock import Mocker

    from parsons.solidarity_tech import SolidarityTech

ENDPOINT = "pages"


class TestGetPages:
    @pytest.mark.vcr
    def test_get_pages_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_pages` returns both a Table of results and the associated metadata."""
        pages, pages_meta = st.get_pages()

        assert isinstance(pages, Table)
        assert pages.name == "Solidarity Tech Pages"
        assert len(pages) > 0
        assert isinstance(pages[0], dict)

        assert isinstance(pages_meta, dict)
        assert pages_meta["total_count"] > 0
        assert pages_meta["limit"] == 20
        assert pages_meta["offset"] == 0

    def test_get_pages_minimal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_pages` makes the appropriate calls."""
        endpoint_url = (
            f"{st.api_url}{ENDPOINT}?_limit=20&_offset=0&_since=0&include_action_counts=False"
        )
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _ = st.get_pages()

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url

    def test_get_pages_maximal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_pages` makes the appropriate calls."""
        limit = 30
        offset = 5
        since = 1788075104
        include_action_counts = True
        endpoint_url = f"{st.api_url}{ENDPOINT}?_limit={limit}&_offset={offset}&_since={since}&include_action_counts={include_action_counts}"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _ = st.get_pages(
            limit=limit,
            offset=offset,
            since=since,
            include_action_counts=include_action_counts,
        )

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url


class TestGetPage:
    @pytest.mark.vcr
    def test_get_page_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_page` returns both a Table of results and the associated metadata."""
        resource_id = 774
        page, page_meta = st.get_page(resource_id=resource_id)

        assert isinstance(page, dict)
        assert page["id"] == resource_id

        assert isinstance(page_meta, dict)
        assert page_meta["total_count"] > 0
        assert page_meta["limit"] == 1
        assert page_meta["offset"] == 0

    def test_get_page_minimal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_page` makes the appropriate calls."""
        resource_id = 960
        endpoint_url = f"{st.api_url}{ENDPOINT}/{resource_id}?include_action_counts=False"
        _ = requests_mock.get(endpoint_url, json={"data": {}, "meta": {}})

        _, _ = st.get_page(resource_id=resource_id)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url

    def test_get_page_maximal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_page` makes the appropriate calls."""
        resource_id = 960
        include_action_counts = True
        endpoint_url = (
            f"{st.api_url}{ENDPOINT}/{resource_id}?include_action_counts={include_action_counts}"
        )
        _ = requests_mock.get(endpoint_url, json={"data": {}, "meta": {}})

        _, _ = st.get_page(resource_id=resource_id, include_action_counts=include_action_counts)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url
