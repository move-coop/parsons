import unittest
import os
import requests_mock
from parsons import VAN
from requests.exceptions import HTTPError
from test.test_van.responses_people import (
    find_people_response,
    get_person_response,
    merge_contacts_response,
    delete_person_response,
)

os.environ["VAN_API_KEY"] = "SOME_KEY"


class TestNGPVAN(unittest.TestCase):
    def setUp(self):
        self.van = VAN(os.environ["VAN_API_KEY"], db="MyVoters", raise_for_status=False)

    @requests_mock.Mocker()
    def test_find_person(self, m):
        m.post(
            self.van.connection.uri + "people/find",
            json=find_people_response,
            status_code=200,
        )

        person = self.van.find_person(first_name="Bob", last_name="Smith", phone=4142020792)

        self.assertEqual(person, find_people_response)

    @requests_mock.Mocker()
    def test_find_person_json(self, m):
        json = {
            "firstName": "Bob",
            "lastName": "Smith",
            "phones": [{"phoneNumber": 4142020792}],
        }

        m.post(
            self.van.connection.uri + "people/find",
            json=find_people_response,
            status_code=200,
        )

        person = self.van.find_person_json(match_json=json)

        self.assertEqual(person, find_people_response)

    def test_upsert_person(self):
        pass

    def test_upsert_person_json(self):
        pass

    def test_update_person(self):
        pass

    def test_update_person_json(self):
        pass

    def test_people_search(self):
        # Already tested as part of upsert and find person methods
        pass

    def test_valid_search(self):
        # Fails with FN / LN Only
        self.assertRaises(
            ValueError,
            self.van._valid_search,
            "Barack",
            "Obama",
            None,
            None,
            None,
            None,
            None,
        )

        # Fails with only Zip
        self.assertRaises(
            ValueError,
            self.van._valid_search,
            "Barack",
            "Obama",
            None,
            None,
            None,
            None,
            60622,
        )

        # Fails with no street number
        self.assertRaises(
            ValueError,
            self.van._valid_search,
            "Barack",
            "Obama",
            None,
            None,
            None,
            "Pennsylvania Ave",
            None,
        )

        # Successful with FN/LN/Email
        self.van._valid_search("Barack", "Obama", "barack@email.com", None, None, None, None)

        # Successful with FN/LN/DOB/ZIP
        self.van._valid_search(
            "Barack", "Obama", "barack@email.com", None, "2000-01-01", None, 20009
        )

        # Successful with FN/LN/Phone
        self.van._valid_search("Barack", "Obama", None, 2024291000, None, None, None)

    @requests_mock.Mocker()
    def test_get_person(self, m):
        json = get_person_response

        # Test works with external ID
        m.get(self.van.connection.uri + "people/DWID:15406767", json=json)
        person = self.van.get_person("15406767", id_type="DWID")
        self.assertEqual(get_person_response, person)

        # Test works with vanid
        m.get(self.van.connection.uri + "people/19722445", json=json)
        person = self.van.get_person("19722445")
        self.assertEqual(get_person_response, person)

    @requests_mock.Mocker()
    def test_delete_person(self, m):
        json = delete_person_response
        # Test works with vanid
        m.delete(self.van.connection.uri + "people/19722445", json=json)
        response = self.van.delete_person("19722445")
        self.assertEqual(delete_person_response, response)

    @requests_mock.Mocker()
    def test_apply_canvass_result(self, m):
        # Test a valid attempt
        m.post(self.van.connection.uri + "people/2335282/canvassResponses", status_code=204)
        self.van.apply_canvass_result(2335282, 18)

        # Test a bad result code
        json = {
            "errors": [
                {
                    "code": "INVALID_PARAMETER",
                    "text": "'resultCodeId' must be a valid result code in the current context.",
                    "properties": ["resultCodeId"],
                }
            ]
        }
        m.post(
            self.van.connection.uri + "people/2335282/canvassResponses",
            json=json,
            status_code=400,
        )
        self.assertRaises(HTTPError, self.van.apply_canvass_result, 2335282, 0)

        # Test a bad vanid
        json = {
            "errors": [
                {
                    "code": "INTERNAL_SERVER_ERROR",
                    "text": "An unknown error occurred",
                    "referenceCode": "88A111-E2FF8",
                }
            ]
        }
        m.post(
            self.van.connection.uri + "people/0/canvassResponses",
            json=json,
            status_code=400,
        )
        self.assertRaises(HTTPError, self.van.apply_canvass_result, 0, 18)

        # Test a good dwid
        m.post(
            self.van.connection.uri + "people/DWID:2335282/canvassResponses",
            status_code=204,
        )
        self.van.apply_canvass_result(2335282, 18, id_type="DWID")

        # test canvassing via phone or sms without providing phone number
        self.assertRaises(Exception, self.van.apply_canvass_result, 2335282, 18, contact_type_id=37)

        # test canvassing via phone or sms with providing phone number
        m.post(self.van.connection.uri + "people/2335282/canvassResponses", status_code=204)
        self.van.apply_canvass_result(2335282, 18, contact_type_id=37, phone="(516)-555-2342")

    @requests_mock.Mocker()
    def test_apply_survey_question(self, m):
        # Test valid survey question
        m.post(self.van.connection.uri + "people/2335282/canvassResponses", status_code=204)
        self.van.apply_survey_response(2335282, 351006, 1443891)

        # Test bad survey response id
        # json = {
        #     'errors': [{
        #         'code': 'INVALID_PARAMETER',
        #         'text': ("'surveyResponseId' must be a valid Response to the given "
        #                  "Survey Question."),
        #         'properties': ['responses[0].surveyResponseId']
        #     }]
        # }
        m.post(self.van.connection.uri + "people/2335282/canvassResponses", status_code=400)
        self.assertRaises(HTTPError, self.van.apply_survey_response, 2335282, 0, 1443891)

        # Test bad survey question id
        # json = {
        #     'errors': [{
        #         'code': 'INVALID_PARAMETER',
        #         'text': ("'surveyQuestionId' must be a valid Survey Question that is "
        #                 "available in the current context."),
        #         'properties': ['responses[0].surveyQuestionId']
        #     }]
        # }
        m.post(self.van.connection.uri + "people/2335282/canvassResponses", status_code=400)
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
        m.post(
            self.van.connection.uri + "people/{}/relationships".format(bad_vanid_1),
            status_code=404,
        )

        # Good request
        m.post(
            self.van.connection.uri + "people/{}/relationships".format(good_vanid_1),
            status_code=204,
        )

        # Test bad input
        self.assertRaises(
            HTTPError,
            self.van.create_relationship,
            bad_vanid_1,
            vanid_2,
            relationship_id,
        )
        self.assertRaises(
            HTTPError,
            self.van.create_relationship,
            bad_vanid_1,
            vanid_2,
            relationship_id,
        )

        self.van.create_relationship(good_vanid_1, vanid_2, relationship_id)

    @requests_mock.Mocker()
    def test_apply_person_code(self, m):
        vanid = 999
        code_id = 888

        # Test good request
        m.post(self.van.connection.uri + f"people/{vanid}/codes", status_code=204)
        self.van.apply_person_code(vanid, code_id)

        # Test bad request
        m.post(self.van.connection.uri + f"people/{vanid}/codes", status_code=404)
        self.assertRaises(HTTPError, self.van.apply_person_code, vanid, code_id)

    @requests_mock.Mocker()
    def test_merge_contacts(self, m):
        source_vanid = 12345

        m.put(
            self.van.connection.uri + f"people/{source_vanid}/mergeInto",
            json=merge_contacts_response,
            status_code=200,
        )

        person = self.van.merge_contacts(source_vanid=source_vanid, primary_vanid=56789)

        self.assertEqual(person, merge_contacts_response)
