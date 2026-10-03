"""Tests for the Custom User Properties methods of :class:`~parsons.solidarity_tech.SolidarityTech`."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest

from parsons import Table
from parsons.solidarity_tech import solidarity_tech_datatypes

if TYPE_CHECKING:
    from requests_mock import Mocker

    from parsons.solidarity_tech import SolidarityTech

ENDPOINT = "custom_user_properties"


class TestGetCustomUserProperties:
    @pytest.mark.vcr
    def test_get_custom_user_properties_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_custom_user_properties` returns both a Table of results and the associated metadata."""
        custom_user_properties, custom_user_properties_meta = st.get_custom_user_properties()

        assert isinstance(custom_user_properties, Table)
        assert custom_user_properties.name == "Solidarity Tech Custom User Properties"
        assert len(custom_user_properties) > 0
        assert isinstance(custom_user_properties[0], dict)

        assert isinstance(custom_user_properties_meta, dict)
        assert custom_user_properties_meta["total_count"] > 0
        assert custom_user_properties_meta["limit"] == 20
        assert custom_user_properties_meta["offset"] == 0

    def test_get_custom_user_properties_minimal(
        self, st: SolidarityTech, requests_mock: Mocker
    ) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_custom_user_properties` makes the appropriate calls."""
        endpoint_url = f"{st.api_url}{ENDPOINT}?_limit=20&_offset=0&_since=0"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _, _ = st.get_custom_user_properties()

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url

    def test_get_custom_user_properties_maximal(
        self, st: SolidarityTech, requests_mock: Mocker
    ) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_custom_user_properties` makes the appropriate calls."""
        limit = 30
        offset = 5
        since = 1788075104
        scope_id = 29775
        scope_type = solidarity_tech_datatypes.ScopeType.CHAPTER
        endpoint_url = f"{st.api_url}{ENDPOINT}?_limit={limit}&_offset={offset}&_since={since}&scope_id={scope_id}&scope_type={scope_type.value}"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _, _ = st.get_custom_user_properties(
            limit=limit, offset=offset, since=since, scope_id=scope_id, scope_type=scope_type
        )

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url


class TestCreateCustomUserProperty:
    @pytest.mark.vcr
    def test_create_custom_user_property_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.create_custom_user_property` returns the data for the created custom user property."""
        label = "TestCheckbox261007"
        field_type = solidarity_tech_datatypes.FieldType.CHECKBOX
        custom_user_property = st.create_custom_user_property(label=label, field_type=field_type)

        assert isinstance(custom_user_property["id"], int)
        assert custom_user_property["name"] == label
        assert custom_user_property["field_type"] == field_type.value

    def test_create_custom_user_property_minimal(
        self, st: SolidarityTech, requests_mock: Mocker
    ) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.create_custom_user_property` makes the appropriate calls."""
        label = "TestCheckbox260907"
        field_type = solidarity_tech_datatypes.FieldType.CHECKBOX
        endpoint_url = f"{st.api_url}{ENDPOINT}"
        _ = requests_mock.post(endpoint_url, status_code=HTTPStatus.CREATED, json={"data": {}})

        _ = st.create_custom_user_property(label=label, field_type=field_type)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "POST"
        assert requests_mock.last_request.url == endpoint_url
        assert requests_mock.last_request.json()["label"] == label
        assert requests_mock.last_request.json()["field_type"] == field_type.value

    def test_create_custom_user_property_maximal(
        self, st: SolidarityTech, requests_mock: Mocker
    ) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.create_custom_user_property` makes the appropriate calls."""
        label = "TestCheckbox260907"
        field_type = solidarity_tech_datatypes.FieldType.INPUT
        description = "Just trying this out"
        options = [{"label": {"en": "Knock Doors"}, "value": "canvass"}]
        scope_type = solidarity_tech_datatypes.ScopeType.ORGANIZATION
        scope_id = 123
        endpoint_url = f"{st.api_url}{ENDPOINT}"
        _ = requests_mock.post(endpoint_url, status_code=HTTPStatus.CREATED, json={"data": {}})

        _ = st.create_custom_user_property(
            label=label,
            field_type=field_type,
            description=description,
            options=options,
            scope_type=scope_type,
            scope_id=scope_id,
        )

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "POST"
        assert requests_mock.last_request.url == endpoint_url
        assert requests_mock.last_request.json()["label"] == label
        assert requests_mock.last_request.json()["field_type"] == field_type.value
        assert requests_mock.last_request.json()["description"] == description
        assert requests_mock.last_request.json()["options"] == options
        assert requests_mock.last_request.json()["scope_type"] == scope_type.value
        assert requests_mock.last_request.json()["scope_id"] == scope_id


class TestDeleteCustomUserPropertyOption:
    @pytest.mark.vcr
    def test_delete_custom_user_property_option_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.delete_custom_user_property_option` returns the data for the deleted custom user property."""
        custom_user_property_id = 5239
        resource_id = "8PNwFZgr"

        custom_user_property = st.delete_custom_user_property_option(
            custom_user_property_id=custom_user_property_id, resource_id=resource_id
        )

        assert isinstance(custom_user_property["id"], int)
        assert custom_user_property["id"] == custom_user_property_id
        assert custom_user_property["options"] is not None
        assert all(option["value"] != resource_id for option in custom_user_property["options"])

    def test_delete_custom_user_property_option(
        self, st: SolidarityTech, requests_mock: Mocker
    ) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.delete_custom_user_property_option` makes the appropriate calls."""
        custom_user_property_id = 25987123
        resource_id = "canvass"
        endpoint_url = f"{st.api_url}{ENDPOINT}/{custom_user_property_id}/options/{resource_id}"
        _ = requests_mock.delete(endpoint_url, json={"data": {}})

        _ = st.delete_custom_user_property_option(
            custom_user_property_id=custom_user_property_id, resource_id=resource_id
        )

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "DELETE"
        assert requests_mock.last_request.url == endpoint_url


class TestCreateCustomUserPropertyOption:
    @pytest.mark.vcr
    def test_create_custom_user_property_option_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.create_custom_user_property_option` returns the data for the created custom user property."""
        resource_id = 5239
        label = [{"en": "d97c8h3"}]

        custom_user_property = st.create_custom_user_property_option(
            resource_id=resource_id, label=label
        )

        assert isinstance(custom_user_property["id"], int)
        assert custom_user_property["id"] == resource_id
        assert custom_user_property["options"] is not None
        assert any(option["label"] == label for option in custom_user_property["options"])

    def test_create_custom_user_property_option(
        self, st: SolidarityTech, requests_mock: Mocker
    ) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.create_custom_user_property_option` makes the appropriate calls."""
        resource_id = 5239
        label = [{"en": "option_name"}]
        value = "internal_name"
        endpoint_url = f"{st.api_url}{ENDPOINT}/{resource_id}/options"
        _ = requests_mock.post(endpoint_url, status_code=HTTPStatus.CREATED, json={"data": {}})

        _ = st.create_custom_user_property_option(resource_id=resource_id, label=label, value=value)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "POST"
        assert requests_mock.last_request.url == endpoint_url
        assert requests_mock.last_request.json()["label"] == label
        assert requests_mock.last_request.json()["value"] == value
