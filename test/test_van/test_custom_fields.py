import unittest
import os
import requests_mock
from parsons import VAN
from test.utils import assert_matching_tables


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

os.environ["VAN_API_KEY"] = "SOME_KEY"


class TestCustomFields(unittest.TestCase):
    def setUp(self):

        self.van = VAN(os.environ["VAN_API_KEY"], db="MyVoters")

    @requests_mock.Mocker()
    def test_get_custom_fields(self, m):

        m.get(self.van.connection.uri + "customFields", json=custom_field)
        assert_matching_tables(custom_field, self.van.get_custom_fields())

    @requests_mock.Mocker()
    def test_get_custom_field_values(self, m):

        m.get(self.van.connection.uri + "customFields", json=custom_field)
        assert_matching_tables(custom_field_values, self.van.get_custom_fields_values())

    @requests_mock.Mocker()
    def test_get_custom_field(self, m):

        m.get(self.van.connection.uri + "customFields/157", json=custom_field)
        assert_matching_tables(custom_field, self.van.get_custom_field(157))
