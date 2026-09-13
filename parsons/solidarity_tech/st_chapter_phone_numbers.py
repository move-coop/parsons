"""Connector class for interacting with the SolidarityTech Chapter Phone Numbers endpoint."""

from __future__ import annotations

import logging
from http import HTTPStatus
from typing import TYPE_CHECKING

from parsons import Table
from parsons.solidarity_tech.base import SolidarityTechBase

if TYPE_CHECKING:
    from datetime import datetime

    from parsons.solidarity_tech.datatypes import ChapterPhoneNumberData, Metadata
    from parsons.utilities.api_connector import _JsonType

logger = logging.getLogger(__name__)


class SolidarityTechChapterPhoneNumbers(SolidarityTechBase):
    """Methods for interacting with the SolidarityTech chapter phone numbers endpoint."""

    def get_chapter_phone_numbers(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
        chapter_id: int | None = None,
    ) -> tuple[Table, Metadata]:
        """
        Retrieve a list of chapter phone numbers.

        Args:
            limit:
                Limits the number of items returned.
                Default is 20, maximum is 100.
            offset:
                Number of items to skip before starting to return the results.
            since:
                UTC timestamp in seconds since the Unix epoch to filter calls created after this time.
            chapter_id:
                Filters chapter phone numbers by chapter_id within the accessible scope.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            All the chapter phone numbers entries.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_chapter-phone-numbers>`__

        """
        params: dict[str, _JsonType] = {}
        _ = chapter_id is not None and params.update({"chapter_id": chapter_id})

        res = self._get_resources(
            "chapter_phone_numbers",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
        )

        expected_responses = {HTTPStatus.OK: (True, "chapter phone numbers listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        data: list[ChapterPhoneNumberData] = res.json()["data"]
        meta: Metadata = res.json()["meta"]

        return Table(data, name="Solidarity Tech Chapter Phone Numbers"), meta
