from parsons import VAN
from test.conftest import assert_matching_tables

custom_field = [
    {
        "customFieldId": 157,
        "customFieldParentId": None,
        "customFieldName": "Education level",
        "customFieldGroupId": 52,
        "customFieldGroupName": "Education",
        "customFieldGroupType": "Contacts",
        "customFieldTypeId": "S",
        "isEditable": True,
        "isExportable": False,
        "maxTextboxCharacters": None,
        "availableValues": [
            {"id": 1, "name": "High School diploma", "parentValueId": None},
            {"id": 2, "name": "College degree", "parentValueId": None},
            {"id": 3, "name": "Postgraduate degree", "parentValueId": None},
            {"id": 4, "name": "Doctorate", "parentValueId": None},
        ],
    }
]

custom_field_values = [
    {
        "customFieldId": 157,
        "id": 1,
        "name": "High School diploma",
        "parentValueId": None,
    },
    {"customFieldId": 157, "id": 2, "name": "College degree", "parentValueId": None},
    {
        "customFieldId": 157,
        "id": 3,
        "name": "Postgraduate degree",
        "parentValueId": None,
    },
    {"customFieldId": 157, "id": 4, "name": "Doctorate", "parentValueId": None},
]


def test_get_custom_fields(van: VAN, requests_mock):
    requests_mock.get(van.connection.uri + "customFields", json=custom_field)
    assert_matching_tables(custom_field, van.get_custom_fields())


def test_get_custom_field_values(van: VAN, requests_mock):
    requests_mock.get(van.connection.uri + "customFields", json=custom_field)
    assert_matching_tables(custom_field_values, van.get_custom_fields_values())


def test_get_custom_field(van: VAN, requests_mock):
    requests_mock.get(van.connection.uri + "customFields/157", json=custom_field)
    assert_matching_tables(custom_field, van.get_custom_field(157))
