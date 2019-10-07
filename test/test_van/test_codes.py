import unittest
import os
import requests_mock
from parsons.ngpvan.van import VAN
from test.utils import validate_list, assert_matching_tables

os.environ['VAN_API_KEY'] = 'SOME_KEY'


class TestCodes(unittest.TestCase):

    def setUp(self):

        self.van = VAN(os.environ['VAN_API_KEY'], db="MyVoters")

    def tearDown(self):

        pass

    @requests_mock.Mocker()
    def test_get_codes(self, m):

        json = {'items': [{'codeId': 1004916,
                           'parentCodeId': None,
                           'name': 'Data Entry',
                           'description': 'for test.',
                           'codePath': 'Data Entry',
                           'createdByName': '',
                           'dateCreated': '2018-07-13T15:16:00Z',
                           'supportedEntities': None,
                           'codeType': 'Tag',
                           'campaign': None,
                           'contactType': None}],
                'nextPageLink': None, 'count': 8}

        m.get(self.van.connection.uri + 'codes', json=json)
        assert_matching_tables(json['items'],self.van.get_codes())

    @requests_mock.Mocker()
    def test_get_code(self, m):

        json = {'codeId': 1004916,
                'parentCodeId': None,
                'name': 'Data Entry',
                        'description': 'for test.',
                        'codePath': 'Data Entry',
                        'createdByName': 'Barack Obama',
                        'dateCreated': '2018-07-13T15:16:00Z',
                        'supportedEntities': [{'name': 'Contacts',
                                               'isSearchable': True,
                                               'isApplicable': True}],
                        'codeType': 'Tag',
                        'campaign': None,
                        'contactType': None}

        m.get(self.van.connection.uri + 'codes/1004916', json=json)

        expected = ['codeId', 'parentCodeId', 'name', 'description', 'codePath',
                    'createdByName', 'dateCreated', 'supportedEntities', 'codeType',
                    'campaign', 'contactType']

        # Assert response is expected structure
        self.assertTrue(validate_list(expected, self.van.get_code(1004916)))

    @requests_mock.Mocker()
    def test_get_code_types(self, m):

        json = ['Tag', 'SourceCode']
        m.get(self.van.connection.uri + 'codeTypes', json=json)
        self.assertEqual(json, self.van.get_code_types())

    @requests_mock.Mocker()
    def test_create_code(self, m):

        m.post(self.van.connection.uri + 'codes', json=1004960)

        # Test that it doesn't throw and error
        r = self.van.create_code('Test Code', supported_entities=[{'name': 'Events',
                                                                   'is_searchable': True,
                                                                   'is_applicable': True}])

        self.assertEqual(r, 1004960)

    @requests_mock.Mocker()
    def test_update_code(self, m):

        m.put(self.van.connection.uri + 'codes/1004960', status_code=204)

        # Test that it doesn't throw and error
        r = self.van.update_code(1004960, name='Test')

        # Assert that it returns the right code
        self.assertEqual(r[0], 204)

    @requests_mock.Mocker()
    def test_delete_code(self, m):

        m.delete(self.van.connection.uri + 'codes/1004960', status_code=204)

        # Test that it doesn't throw and error
        r = self.van.delete_code(1004960)

        # Assert that it returns the right code
        self.assertEqual(r[0], 204)

    @requests_mock.Mocker()
    def test_get_code_supported_entities(self, m):

        json = ['Contacts', 'Events', 'Locations']
        m.get(self.van.connection.uri + 'codes/supportedEntities', json=json)
        self.assertEqual(json, self.van.get_code_supported_entities())
