"""Connector class for interacting with the SolidarityTech Pages endpoint."""

from __future__ import annotations

import logging
from http import HTTPStatus
from typing import TYPE_CHECKING

from parsons import Table
from parsons.solidarity_tech.base import SolidarityTechBase

if TYPE_CHECKING:
    from datetime import datetime

    from parsons.solidarity_tech.datatypes import Metadata, PageData
    from parsons.utilities.api_connector import _JsonType

logger = logging.getLogger(__name__)


class SolidarityTechPages(SolidarityTechBase):
    """Methods for interacting with the SolidarityTech pages endpoint."""

    def get_pages(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
        *,
        include_action_counts: bool = False,
    ) -> tuple[Table, Metadata]:
        """
        Retrieve a list of pages.

        Args:
            limit:
                Limits the number of items returned.
                Default is 20, maximum is 100.
            offset:
                Number of items to skip before starting to return the results.
            since:
                UTC timestamp in seconds since the Unix epoch to filter calls created after this time.
            include_action_counts:
                If True, each page includes ``action_count`` (total submissions) and ``action_goal``
                (the next milestone the public progress bar would display for that count).
                Default is False.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            All the pages.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_pages>`__

        """
        params: dict[str, _JsonType] = {"include_action_counts": include_action_counts}

        res = self._get_resources(
            "pages",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
        )

        expected_responses = {HTTPStatus.OK: (True, "pages listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        data: list[PageData] = res.json()["data"]
        meta: Metadata = res.json()["meta"]

        return Table(data, name="Solidarity Tech Pages"), meta

    def get_page(
        self,
        resource_id: int,
        *,
        include_action_counts: bool = False,
    ) -> tuple[PageData, Metadata]:
        """
        Retrieve a single page.

        Args:
            resource_id:
                ID of the page to retrieve.
            include_action_counts:
                If True, the page includes ``action_count`` (total submissions) and ``action_goal``
                (the next milestone the public progress bar would display for that count).
                Default is False.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single page entry.

        Raises:
            STFailedResponseError: If the page is not found.
            STUnexpectedResponseError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_pages-id>`__

        """
        params: dict[str, _JsonType] = {"include_action_counts": include_action_counts}

        res = self._get_single_resource("pages", resource_id, params=params)

        expected_responses = {
            HTTPStatus.OK: (True, "page found"),
            HTTPStatus.NOT_FOUND: (False, "page not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        data: PageData = res.json()["data"]
        meta: Metadata = res.json()["meta"]

        return data, meta
