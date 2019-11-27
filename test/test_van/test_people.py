import unittest
import os
import requests_mock
from parsons.ngpvan.van import VAN
from requests.exceptions import HTTPError
from test.test_van.responses_people import *

os.environ['VAN_API_KEY'] = 'SOME_KEY'


class TestNGPVAN(unittest.TestCase):

    def setUp(self):

        self.van = VAN(os.environ['VAN_API_KEY'], db="MyVoters", raise_for_status=False)

    @requests_mock.Mocker()
    def test_find_person(self, m):

        json = find_people_response

        m.post(self.van.connection.uri + 'people/find', json=json, status_code=201)

        person = self.van.find_person(first_name='Bob', last_name='Smith', phone=4142020792)

        self.assertEqual(person, json)

    def test_upsert_person(self):

        pass

    def test_people_search(self):

        # Already tested as part of upsert and find person methods
        pass

    def test_valid_search(self):

        # Fails with FN / LN Only
        self.assertRaises(ValueError, self.van._valid_search, 'Barack',
                          'Obama', None, None, None, None, None, None, None)

        # Fails with only Zip
        self.assertRaises(ValueError, self.van._valid_search, 'Barack',
                          'Obama', None, None, None, None, None, 60622, None)

        # Fails with no street number
        self.assertRaises(ValueError, self.van._valid_search, 'Barack',
                          'Obama', None, None, None, None, 'Pennsylvania Ave', None, None)

        # Successful with FN/LN/Email
        self.van._valid_search('Barack', 'Obama', 'barack@email.com', None, None, None,
                               None, None, None)

        # Successful with FN/LN/DOB/ZIP
        self.van._valid_search('Barack', 'Obama', 'barack@email.com', None, None, '2000-01-01',
                               None, 20009, None)

        # Successful with FN/LN/Phone
        self.van._valid_search('Barack', 'Obama', None, 2024291000, None, None,
                               None, None, None)

        # Successful with match_map FN/LN/Email
        match_map_1 = {'firstName': 'Barack', 'lastName': 'Obama', 'emails': [{'email': 'barack@email.com'}]}

        self.van._valid_search(None, None, None, None, None, None,
                               None, None, match_map_1)

        # Successful with match_map FN/LN/Phone
        match_map_2 = {'firstName': 'Barack', 'lastName': 'Obama', 'phones': [{'phoneNumber': 2024291000}]}

        self.van._valid_search(None, None, None, None, None, None,
                               None, None, match_map_2)

        # Successful with match_map FN/LN/DOB/ZIP
        match_map_3 = {'firstName': 'Barack', 'lastName': 'Obama', 'addresses': [{'zipOrPostalCode': 20009}], 'dateOfBirth': '2000-01-01'}

        self.van._valid_search(None, None, None, None, None, None,
                               None, None, match_map_3)

        # Successful with match_map FN/LN/STREETNAME/STREETNUMBER/ZIP
        match_map_4 = {
            'firstName': 'Barack',
            'lastName': 'Obama',
            'addresses':
            [{
                'zipOrPostalCode': 20009,
                'addressLine1': 'glenwood drive'
            }]
        }

        self.van._valid_search(None, None, None, None, None, None,
                               None, None, match_map_4)

        # Successful with match_map Email
        match_map_5 = {'emails': [{'email': 'barack@email.com'}]}

        self.van._valid_search(None, None, None, None, None, None,
                               None, None, match_map_5)

        # Fail with match_map no Email
        match_map_6 = {'firstName': 'Barack', 'lastName': 'Obama'}

        self.van._valid_search(None, None, None, None, None, None,
                               None, None, match_map_5)

        self.assertRaises(ValueError, self.van._valid_search, None, None, None, None, None, None,
                          None, None, match_map_6)

    @requests_mock.Mocker()
    def test_get_person(self, m):

        json = get_person_response

        # Test works with external ID
        m.get(self.van.connection.uri + f'people/DWID:15406767', json=json)
        person = self.van.get_person('15406767', id_type='DWID')
        self.assertEqual(get_person_response, person)

        # Test works with vanid
        m.get(self.van.connection.uri + f'people/19722445', json=json)
        person = self.van.get_person('19722445')
        self.assertEqual(get_person_response, person)

    @requests_mock.Mocker()
    def test_apply_canvass_result(self, m):

        # Test a valid attempt
        m.post(self.van.connection.uri + f'people/2335282/canvassResponses', status_code=204)
        self.van.apply_canvass_result(2335282, 18)

        # Test a bad result code
        json = {'errors':
                [{'code': 'INVALID_PARAMETER',
                    'text': "'resultCodeId' must be a valid result code in the current context.",
                    'properties': ['resultCodeId']}
                 ]}
        m.post(self.van.connection.uri + f'people/2335282/canvassResponses',
               json=json, status_code=400)
        self.assertRaises(HTTPError, self.van.apply_canvass_result, 2335282, 0)

        # Test a bad vanid
        json = {'errors':
                [{'code': 'INTERNAL_SERVER_ERROR',
                  'text': 'An unknown error occurred',
                  'referenceCode': '88A111-E2FF8'}
                 ]}
        m.post(self.van.connection.uri + f'people/0/canvassResponses', json=json, status_code=400)
        self.assertRaises(HTTPError, self.van.apply_canvass_result, 0, 18)

        # Test a good dwid
        m.post(self.van.connection.uri + f'people/DWID:2335282/canvassResponses', status_code=204)
        self.van.apply_canvass_result(2335282, 18, id_type='DWID')

    @requests_mock.Mocker()
    def test_apply_survey_question(self, m):

        # Test valid survey question
        m.post(self.van.connection.uri + f'people/2335282/canvassResponses', status_code=204)
        self.van.apply_survey_response(2335282, 351006, 1443891)

        # Test bad survey response id
        json = {'errors':
                [{'code': 'INVALID_PARAMETER',
                  'text': "'surveyResponseId' must be a valid Response to the given Survey Question.",
                  'properties': ['responses[0].surveyResponseId']}
                 ]}
        m.post(self.van.connection.uri + f'people/2335282/canvassResponses', status_code=400)
        self.assertRaises(HTTPError, self.van.apply_survey_response, 2335282, 0, 1443891)

        # Test bad survey question id
        json = {'errors':
                [{'code': 'INVALID_PARAMETER',
                  'text': "'surveyQuestionId' must be a valid Survey Question that is available in the current context.",
                  'properties': ['responses[0].surveyQuestionId']}]}
        m.post(self.van.connection.uri + f'people/2335282/canvassResponses', status_code=400)
        self.assertRaises(HTTPError, self.van.apply_survey_response, 2335282, 351006, 0)

    def test_toggle_volunteer_action(self):

        pass

    def test_apply_response(self):

        pass

    @requests_mock.Mocker()
    def test_create_relationship(self, m):

        relationship_id = 12
        bad_vanid_1 = 99999
        good_vanid_1 = 12345
        vanid_2 = 54321

        # Bad request
        m.post(self.van.connection.uri + "people/{}/relationships".format(bad_vanid_1),
               status_code=404)

        # Good request
        m.post(self.van.connection.uri + "people/{}/relationships".format(good_vanid_1),
               status_code=204)

        # Test bad input
        self.assertRaises(HTTPError, self.van.create_relationship, bad_vanid_1, vanid_2, relationship_id)
        self.assertRaises(HTTPError, self.van.create_relationship, bad_vanid_1, vanid_2, relationship_id)

        self.van.create_relationship(good_vanid_1, vanid_2, relationship_id)
