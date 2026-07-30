import logging
from datetime import datetime

import numpy as np

from parsons.solidarity_tech.exceptions import STUnexpectedResponseCodeError
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
    ) -> str:
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

        if res.status_code != 200:
            raise STUnexpectedResponseCodeError(res)

        return res.text

    def get_text_template(
        self,
        id: int,
    ) -> str:
        """
        Retrieve a single text template.

        Args:
            id:
                ID of the text template to retrieve.

        Returns:
            A single text template.

        Raises:
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_text-templates-id>`__

        """
        res = self._get_single_resource("text_templates", id)

        if res.status_code not in (200, 404):
            raise STUnexpectedResponseCodeError(res)

        return res.text

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

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Raises:
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

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

        if res.status_code not in (201, 404):
            raise STUnexpectedResponseCodeError(res)

        return res.status_code == 201

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

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Raises:
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

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

        if res.status_code not in (200, 404):
            raise STUnexpectedResponseCodeError(res)

        return res.status_code == 200

    def delete_text_template(
        self,
        id: int,
    ) -> bool:
        """
        Delete an text template with the specified ID.

        Args:
            id:
                Identifier of the text template to delete.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Raises:
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/delete_text-templates-id>`__

        """
        res = self._del_request("text_templates", id)

        if res and res.status_code != 404:
            raise STUnexpectedResponseCodeError(res)

        return not res.status_code
