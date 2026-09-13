"""Connector class for interacting with the SolidarityTech Chapters endpoint."""

from __future__ import annotations

import logging
from http import HTTPStatus
from typing import TYPE_CHECKING

from parsons import Table
from parsons.solidarity_tech.base import SolidarityTechBase

if TYPE_CHECKING:
    from datetime import datetime

    from parsons.solidarity_tech.datatypes import ChapterData, Metadata


logger = logging.getLogger(__name__)


class SolidarityTechChapters(SolidarityTechBase):
    """Methods for interacting with the SolidarityTech chapters endpoint."""

    def get_chapters(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
    ) -> tuple[Table, Metadata]:
        """
        Retrieve a list of chapters.

        Args:
            limit:
                Limits the number of items returned.
                Default is 20, maximum is 100.
            offset:
                Number of items to skip before starting to return the results.
            since:
                UTC timestamp in seconds since the Unix epoch to filter chapters created after this time.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            All the chapters entries.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_chapters>`__

        """
        res = self._get_resources(
            "chapters",
            limit=limit,
            offset=offset,
            since=since,
            additional_headers={"accept": "application/json"},
        )

        expected_responses = {HTTPStatus.OK: (True, "successful")}
        self._handle_status_codes(res=res, codes=expected_responses)

        data: list[ChapterData] = res.json()["data"]
        meta: Metadata = res.json()["meta"]

        return Table(data, name="Solidarity Tech Chapters"), meta
