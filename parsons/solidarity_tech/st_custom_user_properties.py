import logging
from datetime import datetime

from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase
from parsons.solidarity_tech.solidarity_tech_literals import FieldType, ScopeType

logger = logging.getLogger(__name__)


class SolidarityTechCustomUserProperties(SolidarityTechBase):
    def get_custom_user_properties(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
        scope_id: int | None = None,
        scope_type: ScopeType | None = None,
    ) -> str:
        """
        Retrieve a list of custom user properties.

        Args:
            limit:
                Limits the number of items returned. Default is 20, maximum is 100.
            offset:
                Number of items to skip before starting to return the results.
            since:
                UTC timestamp in seconds since the Unix epoch to filter calls created after this time.
            scope_id:
                ID of the scope to filter custom user properties by.
            scope_type:
                Type of the scope to filter custom user properties by.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            All the custom user properties entries

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_custom-user-properties>`__

        """
        params = {"scope_id": scope_id, "scope_type": scope_type}
        res = self._get_resources(
            "custom_user_properties",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
            additional_headers={"accept": "application/json"},
        )

        expected_responses = {200: (True, "successful")}
        self._handle_status_codes(res=res, codes=expected_responses)

        return res.text

    def create_custom_user_property(
        self,
        label: str,
        field_type: FieldType,
        description: str | None = None,
        options: list[dict[str, str | dict[str, str]]] | None = None,
        scope_type: ScopeType | None = None,
        scope_id: int | None = None,
    ) -> bool:
        """
        Create a custom user property.

        Args:
            label:
                Display label for the property.
            description:
                Optional description of the property.
            field_type:
                Type of field for data entry.
            options:
                Options for select, radios, checkbox, or checkboxes field types.
                See documentation.
            scope_type:
                Type of scope for the property.
            scope_id:
                ID of the scope for the property.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_custom-user-properties>`__

        """
        payload = {
            "label": label,
            "description": description,
            "field_type": field_type,
            "options": options,
            "scope_type": scope_type,
            "scope_id": scope_id,
        }
        res = self._post_request(
            "custom_user_properties",
            payload=payload,
            additional_headers={"accept": "application/json", "content-type": "application/json"},
        )

        expected_responses = {
            201: (True, "created"),
            422: (False, "validation failed"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)

    def delete_custom_user_property_option(
        self,
        custom_user_property_id: int,
        id: str,
    ) -> bool:
        """
        Remove an option from a custom user property.

        Args:
            custom_user_property_id:
                Custom user property ID
            id:
                Value of the option to remove

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/delete_custom-user-properties-custom-user-property-id-options-id>`__

        """
        res = self._del_request(
            "custom_user_properties",
            f"{custom_user_property_id}/options/{id}",
            additional_headers={"accept": "application/json"},
        )

        expected_responses = {
            200: (True, "option removed"),
            404: (False, "option or custom user property not found"),
            422: (False, "validation failed"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)

    def create_custom_user_property_option(
        self,
        id: int,
        label: list[dict[str, str | dict[str, str]]],
        value: str | None = None,
    ) -> bool:
        """
        Create an option for a custom user property.

        Args:
            id:
                Custom user property ID
            label:
                Multi-language labels for the option
                See documentation
            value:
                Internal value for the option (will be auto-generated if not provided)

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_custom-user-properties-id-options>`__

        """
        payload = {
            "label": label,
            "value": value,
        }
        res = self._post_request(
            f"custom_user_properties/{id}/options",
            payload=payload,
            additional_headers={"accept": "application/json", "content-type": "application/json"},
        )

        expected_responses = {
            201: (True, "option created"),
            404: (False, "custom user property not found"),
            422: (False, "validation failed"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)
