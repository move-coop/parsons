import unittest
import os
import requests_mock
from parsons.ngpvan.van import VAN
from test.test_van.responses_people import *

os.environ['VAN_API_KEY'] = 'SOME_KEY'


class TestNGPVAN(unittest.TestCase):

    def setUp(self):

        self.van = VAN(os.environ['VAN_API_KEY'], db="MyVoters", raise_for_status=False)

    @requests_mock.Mocker()
    def test_find_person(self, m):

        json = find_people_response

        m.post(self.van.connection.uri + 'people/find', json=json)

        person = self.van.find_person(first_name='Bob', last_name='Smith',
            phone_number=4142020792)

        self.assertEqual(person, json)

    def test_upsert_person(self):

        pass

    def test_people_search(self):

        # Already tested as part of upsert and find person methods
        pass

    def test_valid_search(self):

        # Fails with FN / LN Only
        json = {"firstName": "Barack", "lastName": "Obama"}
        self.assertRaises(ValueError, self.van._valid_search, json)

        # Fails with only Zip
        json.update({"addresses": [{"zipOrPostalCode": 60615}]})
        self.assertRaises(ValueError, self.van._valid_search, json)

        # Fails with street address but no Zip
        del json['addresses'][0]['zipOrPostalCode']
        json['addresses'][0].update({"addressLine1": "5042 S. Woodlawn Ave."})
        self.assertRaises(ValueError, self.van._valid_search, json)

        # Successful with FN/LN/Email
        del json['addresses']
        json.update({"emails": [{"email": "barack@email.com"}]})
        self.van._valid_search(json)

        # Successful with FN/LN/DOB/ZIP
        del json['emails']
        json.update({"addresses": [{"zipOrPostalCode": 60615}], "dateOfBirth": '1961-08-04'})
        self.van._valid_search(json)

        # Successful with FN/LN/Phone
        del json['addresses']
        del json['dateOfBirth']
        json.update({"phones": [{"phoneNumber": 2024291000}]})
        self.van._valid_search(json)

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
        self.assertTrue(self.van.apply_canvass_result(2335282, 18))

        # Test a bad result code
        json = {'errors':
                [{'code': 'INVALID_PARAMETER',
                    'text': "'resultCodeId' must be a valid result code in the current context.",
                    'properties': ['resultCodeId']}
                 ]}
        m.post(self.van.connection.uri + f'people/2335282/canvassResponses',
               json=json, status_code=400)
        self.assertRaises(ValueError, self.van.apply_canvass_result, 2335282, 0)

        # Test a bad vanid
        json = {'errors':
                [{'code': 'INTERNAL_SERVER_ERROR',
                  'text': 'An unknown error occurred',
                  'referenceCode': '88A111-E2FF8'}
                 ]}
        m.post(self.van.connection.uri + f'people/0/canvassResponses', json=json, status_code=400)
        self.assertRaises(ValueError, self.van.apply_canvass_result, 0, 18)

        # Test a good dwid
        m.post(self.van.connection.uri + f'people/DWID:2335282/canvassResponses', status_code=204)
        self.assertTrue(self.van.apply_canvass_result(2335282, 18, id_type='DWID'))

    @requests_mock.Mocker()
    def test_apply_survey_question(self, m):

        # Test valid survey question
        m.post(self.van.connection.uri + f'people/2335282/canvassResponses', status_code=204)
        self.assertTrue(self.van.apply_survey_response(2335282, 351006, 1443891))

        # Test bad survey response id
        json = {'errors':
                [{'code': 'INVALID_PARAMETER',
                  'text': "'surveyResponseId' must be a valid Response to the given Survey Question.",
                  'properties': ['responses[0].surveyResponseId']}
                 ]}
        m.post(self.van.connection.uri + f'people/2335282/canvassResponses', status_code=400)
        self.assertRaises(ValueError, self.van.apply_survey_response, 2335282, 0, 1443891)

        # Test bad survey question id
        json = {'errors':
                [{'code': 'INVALID_PARAMETER',
                  'text': "'surveyQuestionId' must be a valid Survey Question that is available in the current context.",
                  'properties': ['responses[0].surveyQuestionId']}]}
        m.post(self.van.connection.uri + f'people/2335282/canvassResponses', status_code=400)
        self.assertRaises(ValueError, self.van.apply_survey_response, 2335282, 351006, 0)

    @requests_mock.Mocker()
    def test_toggle_activist_code(self, m):

        # Test apply activist code
        m.post(self.van.connection.uri + f'people/2335282/canvassResponses', status_code=204)
        self.assertTrue(self.van.toggle_activist_code(2335282, 4429154, 'apply'))

        # Test remove activist code
        m.post(self.van.connection.uri + f'people/2335282/canvassResponses', status_code=204)
        self.assertTrue(self.van.toggle_activist_code(2335282, 4429154, 'remove'))

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
        self.assertEqual(self.van.create_relationship(bad_vanid_1, vanid_2, relationship_id)[0],
                         404)

        self.assertEqual(self.van.create_relationship(good_vanid_1, vanid_2, relationship_id)[0],
                         204)
