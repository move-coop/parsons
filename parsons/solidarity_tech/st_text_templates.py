import logging
from datetime import datetime

import numpy as np

from parsons import Table
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase
from parsons.solidarity_tech.solidarity_tech_literals import ScopeType

logger = logging.getLogger(__name__)


class SolidarityTechTextTemplates(SolidarityTechBase):
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
        params = {"event_id": event_id}
        res = self._get_resources(
            "text_templates",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
        )

        expected_responses = {200: (True, "text templates listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        return Table(res.json())

    def get_text_template(
        self,
        id: int,
    ) -> dict:
        """
        Retrieve a single text template.

        Args:
            id:
                ID of the text template to retrieve.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single text template.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_text-templates-id>`__

        """
        res = self._get_single_resource("text_templates", id)

        expected_responses = {
            200: (True, "text template found"),
            404: (False, "text template not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        return res.json()

    def create_text_template(
        self,
        scope_id: np.int64,
        scope_type: ScopeType,
        name: str | None = None,
        template: dict[str, str] | None = None,
        event_id: np.int64 | None = None,
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
        payload = {
            "name": name,
            "scope_id": scope_id,
            "scope_type": scope_type,
            "template": template,
            "event_id": event_id,
        }
        res = self._post_request(
            "text_templates",
            payload=payload,
            additional_headers={"content-type": "application/json"},
        )

        expected_responses = {
            201: (True, "text template created"),
            404: (False, "event not found"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)

    def update_text_template(
        self,
        id: int,
        name: str | None = None,
        scope_id: np.int64 | None = None,
        scope_type: ScopeType | None = None,
        template: dict[str, str] | None = None,
        event_id: np.int64 | None = None,
    ) -> bool:
        """
        Update an text template with the specified details.

        Args:
            id:
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
        payload = {
            "name": name,
            "scope_id": scope_id,
            "scope_type": scope_type,
            "template": template,
            "event_id": event_id,
        }
        res = self._put_request(
            "text_templates",
            id,
            payload=payload,
            additional_headers={"content-type": "application/json"},
        )

        expected_responses = {
            200: (True, "text template updated"),
            404: (False, "text template not found"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)

    def delete_text_template(
        self,
        id: int,
    ) -> bool:
        """
        Delete an text template with the specified ID.

        Args:
            id:
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
        res = self._del_request("text_templates", id)

        expected_responses = {404: (False, "text template not found")}
        return self._handle_status_codes(res=res, codes=expected_responses)
