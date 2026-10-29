"""Tests for the Phonebanks methods of :class:`~parsons.solidarity_tech.SolidarityTech`."""

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib import parse

if TYPE_CHECKING:
    from requests_mock import Mocker

    from parsons.solidarity_tech import SolidarityTech

ENDPOINT = "phonebanks"


class TestGetPhonebanks:
    # TODO(bmos): Implement once there is data
    #    @pytest.mark.vcr
    #    def test_get_phonebanks_live(self, st: SolidarityTech) -> None:
    #        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_phonebanks` returns both a Table of results and the associated metadata."""
    #        phonebanks, phonebanks_meta = st.get_phonebanks()
    #
    #        assert isinstance(phonebanks, Table)
    #        assert phonebanks.name == "Solidarity Tech Phonebanks"
    #        assert len(phonebanks) > 0
    #        assert isinstance(phonebanks[0], dict)
    #
    #        assert isinstance(phonebanks_meta, dict)
    #        assert phonebanks_meta["total_count"] > 0
    #        assert phonebanks_meta["limit"] == 20
    #        assert phonebanks_meta["offset"] == 0

    def test_get_phonebanks_minimal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_phonebanks` makes the appropriate calls."""
        endpoint_url = (
            f"{st.api_url}{ENDPOINT}?_limit=20&_offset=0&_since=0&event_id=0&include_stats=False"
        )
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _ = st.get_phonebanks()

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url

    def test_get_phonebanks_maximal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_phonebanks` makes the appropriate calls."""
        limit = 30
        offset = 5
        since = 1788075104
        event_id = 2796
        ids = [287, 12, 23]
        csv_ids = parse.quote_plus(",".join([str(p_id) for p_id in ids]))
        include_stats = True
        endpoint_url = f"{st.api_url}{ENDPOINT}?_limit={limit}&_offset={offset}&_since={since}&event_id={event_id}&include_stats={include_stats}&ids={csv_ids}"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _ = st.get_phonebanks(
            limit=limit,
            offset=offset,
            since=since,
            event_id=event_id,
            ids=ids,
            include_stats=include_stats,
        )

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url


class TestGetPhonebank:
    # TODO(bmos): Implement once there is data
    #    @pytest.mark.vcr
    #    def test_get_phonebank_live(self, st: SolidarityTech) -> None:
    #        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_phonebank` returns the expected data."""
    #        resource_id = 774
    #        phonebank, phonebank_meta = st.get_phonebank(resource_id=resource_id)
    #
    #        assert isinstance(phonebank, dict)
    #        assert phonebank["id"] == resource_id
    #
    #        assert isinstance(phonebank_meta, dict)
    #        assert phonebank_meta["total_count"] > 0
    #        assert phonebank_meta["limit"] == 1
    #        assert phonebank_meta["offset"] == 0

    def test_get_phonebank_minimal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_phonebank` makes the appropriate calls."""
        resource_id = 960
        endpoint_url = f"{st.api_url}{ENDPOINT}/{resource_id}"
        _ = requests_mock.get(endpoint_url, json={"data": {}, "meta": {}})

        _, _ = st.get_phonebank(resource_id=resource_id)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url

    def test_get_phonebank_maximal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_phonebank` makes the appropriate calls."""
        resource_id = 960
        endpoint_url = f"{st.api_url}{ENDPOINT}/{resource_id}"
        _ = requests_mock.get(endpoint_url, json={"data": {}, "meta": {}})

        _, _ = st.get_phonebank(resource_id=resource_id)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url
