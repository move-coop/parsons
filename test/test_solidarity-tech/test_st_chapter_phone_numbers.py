"""Tests for the Chapter Phone Numbers methods of :class:`~parsons.solidarity_tech.SolidarityTech`."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from parsons import Table

if TYPE_CHECKING:
    from requests_mock import Mocker

    from parsons.solidarity_tech import SolidarityTech

ENDPOINT = "chapter_phone_numbers"


class TestGetChapterPhoneNumbers:
    @pytest.mark.vcr
    def test_get_chapter_phone_numbers_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_chapter_phone_numbers` returns both a Table of results and the associated metadata."""
        chapter_phone_numbers, chapter_phone_numbers_meta = st.get_chapter_phone_numbers()

        assert isinstance(chapter_phone_numbers, Table)
        assert chapter_phone_numbers.name == "Solidarity Tech Chapter Phone Numbers"
        assert len(chapter_phone_numbers) > 0
        assert isinstance(chapter_phone_numbers[0], dict)

        assert isinstance(chapter_phone_numbers_meta, dict)
        assert chapter_phone_numbers_meta["total_count"] > 0
        assert chapter_phone_numbers_meta["limit"] == 20
        assert chapter_phone_numbers_meta["offset"] == 0

    def test_get_chapter_phone_numbers_minimal(
        self, st: SolidarityTech, requests_mock: Mocker
    ) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_chapter_phone_numbers` makes the appropriate calls."""
        endpoint_url = f"{st.api_url}{ENDPOINT}?_limit=20&_offset=0&_since=0"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _ = st.get_chapter_phone_numbers()

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url

    def test_get_chapter_phone_numbers_maximal(
        self, st: SolidarityTech, requests_mock: Mocker
    ) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_chapter_phone_numbers` makes the appropriate calls."""
        chapter_id = 982
        limit = 30
        offset = 5
        since = 1788075104
        endpoint_url = f"{st.api_url}{ENDPOINT}?_limit={limit}&_offset={offset}&_since={since}&chapter_id={chapter_id}"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _ = st.get_chapter_phone_numbers(
            chapter_id=chapter_id, limit=limit, offset=offset, since=since
        )

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url
