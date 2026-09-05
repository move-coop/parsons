from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, TypedDict

from parsons import Table
from parsons.solidarity_tech.base import Metadata, SolidarityTechBase

if TYPE_CHECKING:
    from datetime import datetime

    from parsons.solidarity_tech.enums import FieldType, ScopeType
    from parsons.utilities.api_connector import _JsonType

logger = logging.getLogger(__name__)


class UserPropertyDataValue(TypedDict):
    label: dict[str, Any]
    value: str


class UserPropertyData(TypedDict):
    id: int
    name: str
    key: str
    field_type: FieldType
    options: list[UserPropertyDataValue] | None
    scope_id: int | None
    scope_type: ScopeType | None


class SolidarityTechCustomUserProperties(SolidarityTechBase):
    """Methods for interacting with the SolidarityTech custom user properties endpoint."""

    def get_custom_user_properties(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
        scope_id: int | None = None,
        scope_type: ScopeType | None = None,
    ) -> tuple[Table, Metadata]:
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
            All custom user properties entries.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_custom-user-properties>`__

        """
        params: _JsonType = {}
        self._add_if_field_not_empty(params, "scope_id", scope_id)
        self._add_if_field_not_empty(params, "description", scope_type)

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

        data: list[UserPropertyData] = res.json()["data"]
        meta: Metadata = res.json()["meta"]

        return Table(data), meta

    def create_custom_user_property(
        self,
        label: str,
        field_type: FieldType,
        description: str | None = None,
        options: list[dict[str, str | dict[str, str]]] | None = None,
        scope_type: ScopeType | None = None,
        scope_id: int | None = None,
    ) -> UserPropertyData:
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
            Created custom user property entry.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_custom-user-properties>`__

        """
        payload: dict[str, Any] = {"label": label, "field_type": field_type.value}
        self._add_if_field_not_empty(payload, "description", description)
        self._add_if_field_not_empty(payload, "options", options)
        self._add_if_field_not_empty(payload, "scope_type", scope_type)
        self._add_if_field_not_empty(payload, "scope_id", scope_id)

        res = self._post_request(
            "custom_user_properties",
            payload=payload,
            additional_headers={"accept": "application/json", "content-type": "application/json"},
        )

        expected_responses = {
            201: (True, "created"),
            422: (False, "validation failed"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        return res.json()["data"]

    def delete_custom_user_property_option(
        self,
        custom_user_property_id: int,
        resource_id: str,
    ) -> UserPropertyData:
        """
        Remove an option from a custom user property.

        Args:
            custom_user_property_id:
                Custom user property ID
            resource_id:
                Value of the option to remove

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Custom user property entry, as it exists after deleting the option.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/delete_custom-user-properties-custom-user-property-id-options-id>`__

        """
        res = self._del_request(
            "custom_user_properties",
            f"{custom_user_property_id}/options/{resource_id}",
            additional_headers={"accept": "application/json"},
        )

        expected_responses = {
            200: (True, "option removed"),
            404: (False, "option or custom user property not found"),
            422: (False, "validation failed"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        return res.json()["data"]

    def create_custom_user_property_option(
        self,
        resource_id: int,
        label: list[dict[str, str | dict[str, str]]],
        value: str | None = None,
    ) -> UserPropertyData:
        """
        Create an option for a custom user property.

        Args:
            resource_id:
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
            Custom user property entry, as it exists after creating the new option.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_custom-user-properties-id-options>`__

        """
        payload: dict[str, Any] = {"label": label}
        self._add_if_field_not_empty(payload, "value", value)

        res = self._post_request(
            f"custom_user_properties/{resource_id}/options",
            payload=payload,
            additional_headers={"accept": "application/json", "content-type": "application/json"},
        )

        expected_responses = {
            201: (True, "option created"),
            404: (False, "custom user property not found"),
            422: (False, "validation failed"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        return res.json()["data"]
