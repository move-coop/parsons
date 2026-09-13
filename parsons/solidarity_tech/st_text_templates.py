"""Connector class for interacting with the SolidarityTech Text Templates endpoint."""

from __future__ import annotations

import logging
from http import HTTPStatus
from typing import TYPE_CHECKING

from parsons import Table
from parsons.solidarity_tech.base import SolidarityTechBase

if TYPE_CHECKING:
    from datetime import datetime

    from parsons.solidarity_tech.datatypes import ScopeType
    from parsons.utilities.api_connector import _JsonType

logger = logging.getLogger(__name__)


class SolidarityTechTextTemplates(SolidarityTechBase):
    """Methods for interacting with the SolidarityTech text templates endpoint."""

    def get_text_templates(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
        event_id: int = 0,
    ) -> Table:
        """
        Retrieve a list of text templates.

        Args:
            limit:
                Limits the number of items returned.
                Default is 20, maximum is 100.
            offset:
                Number of items to skip before starting to return the results.
            since:
                UTC timestamp in seconds since the Unix epoch to filter calls created after this time.
            event_id:
                Filters rsvps by event_id within the accessible scope.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            All the text templates.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_text-templates>`__

        """
        params: dict[str, _JsonType] = {"event_id": event_id}

        res = self._get_resources(
            "text_templates",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
        )

        expected_responses = {HTTPStatus.OK: (True, "text templates listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        return Table(res.json())

    def get_text_template(
        self,
        resource_id: int,
    ) -> dict:
        """
        Retrieve a single text template.

        Args:
            resource_id:
                ID of the text template to retrieve.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single text template.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_text-templates-id>`__

        """
        res = self._get_single_resource("text_templates", resource_id)

        expected_responses = {
            HTTPStatus.OK: (True, "text template found"),
            HTTPStatus.NOT_FOUND: (False, "text template not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        return res.json()

    def create_text_template(
        self,
        scope_id: int,
        scope_type: ScopeType,
        name: str | None = None,
        template: dict[str, str] | None = None,
        event_id: int | None = None,
    ) -> bool:
        """
        Create an text template with the specified details.

        Args:
            scope_id:
                Identifier for the scope.
            scope_type:
                Type of the scope.
            name:
                Name of the entity.
            template:
                Template content in various languages,
                where keys are 2-character language codes
                (e.g., "en" for English, "fr" for French).
            event_id:
                Identifier for the associated event, if applicable.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_text-templates>`__

        """
        payload: dict[str, _JsonType] = {
            "scope_id": scope_id,
            "scope_type": scope_type,
        }
        name is not None and payload.update({"name": name})
        template is not None and payload.update({"template": template})
        event_id is not None and payload.update({"event_id": event_id})

        res = self._post_request(
            "text_templates",
            payload=payload,
            additional_headers={"content-type": "application/json"},
        )

        expected_responses = {
            HTTPStatus.CREATED: (True, "text template created"),
            HTTPStatus.NOT_FOUND: (False, "event not found"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)

    def update_text_template(
        self,
        resource_id: int,
        name: str | None = None,
        scope_id: int | None = None,
        scope_type: ScopeType | None = None,
        template: dict[str, str] | None = None,
        event_id: int | None = None,
    ) -> bool:
        """
        Update an text template with the specified details.

        Args:
            resource_id:
                Identifier of the text template to update.
            name:
                Name of the entity.
            scope_id:
                Identifier for the scope.
            scope_type:
                Type of the scope.
            template:
                Template content in various languages,
                where keys are 2-character language codes
                (e.g., "en" for English, "fr" for French).
            event_id:
                Identifier for the associated event, if applicable.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/put_text-templates-id>`__

        """
        payload: dict[str, _JsonType] = {}
        name is not None and payload.update({"name": name})
        scope_id is not None and payload.update({"scope_id": scope_id})
        scope_type is not None and payload.update({"scope_type": scope_type})
        template is not None and payload.update({"template": template})
        event_id is not None and payload.update({"event_id": event_id})

        res = self._put_request(
            "text_templates",
            resource_id,
            payload=payload,
            additional_headers={"content-type": "application/json"},
        )

        expected_responses = {
            HTTPStatus.OK: (True, "text template updated"),
            HTTPStatus.NOT_FOUND: (False, "text template not found"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)

    def delete_text_template(
        self,
        resource_id: int,
    ) -> bool:
        """
        Delete an text template with the specified ID.

        Args:
            resource_id:
                Identifier of the text template to delete.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/delete_text-templates-id>`__

        """
        res = self._delete_request("text_templates", resource_id)

        expected_responses = {HTTPStatus.NOT_FOUND: (False, "text template not found")}
        return self._handle_status_codes(res=res, codes=expected_responses)
