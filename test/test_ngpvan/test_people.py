import pytest
from requests.exceptions import HTTPError

from parsons import VAN
from test.test_ngpvan.responses_people import (
    delete_person_response,
    find_people_response,
    get_person_response,
    merge_contacts_response,
)


def test_find_person(van: VAN, requests_mock):
    requests_mock.post(
        van.connection.uri + "people/find",
        json=find_people_response,
        status_code=200,
    )

    person = van.find_person(first_name="Bob", last_name="Smith", phone=4142020792)

    assert person == find_people_response


def test_find_person_json(van: VAN, requests_mock):
    json = {
        "firstName": "Bob",
        "lastName": "Smith",
        "phones": [{"phoneNumber": 4142020792}],
    }

    requests_mock.post(
        van.connection.uri + "people/find",
        json=find_people_response,
        status_code=200,
    )

    person = van.find_person_json(match_json=json)

    assert person == find_people_response


def test_upsert_person():
    pass


def test_upsert_person_json():
    pass


def test_update_person():
    pass


def test_update_person_json():
    pass


def test_people_search():
    # Already tested as part of upsert and find person methods
    pass


def test_valid_search(van: VAN):
    # Fails with FN / LN Only
    with pytest.raises(
        ValueError,
        match="Person find must include the following minimum combinations to conduct a search",
    ):
        van._valid_search(
            "Barack",
            "Obama",
            None,
            None,
            None,
            None,
            None,
        )

    # Fails with only Zip
    with pytest.raises(
        ValueError,
        match="Person find must include the following minimum combinations to conduct a search",
    ):
        van._valid_search(
            "Barack",
            "Obama",
            None,
            None,
            None,
            None,
            60622,
        )

    # Fails with no street number
    with pytest.raises(
        ValueError,
        match="Person find must include the following minimum combinations to conduct a search",
    ):
        van._valid_search(
            "Barack",
            "Obama",
            None,
            None,
            None,
            "Pennsylvania Ave",
            None,
        )

    # Successful with FN/LN/Email
    van._valid_search("Barack", "Obama", "barack@email.com", None, None, None, None)

    # Successful with FN/LN/DOB/ZIP
    van._valid_search("Barack", "Obama", "barack@email.com", None, "2000-01-01", None, 20009)

    # Successful with FN/LN/Phone
    van._valid_search("Barack", "Obama", None, 2024291000, None, None, None)


def test_get_person(van: VAN, requests_mock):
    json = get_person_response

    # Test works with external ID
    requests_mock.get(van.connection.uri + "people/DWID:15406767", json=json)
    person = van.get_person("15406767", id_type="DWID")
    assert get_person_response == person

    # Test works with vanid
    requests_mock.get(van.connection.uri + "people/19722445", json=json)
    person = van.get_person("19722445")
    assert get_person_response == person


def test_delete_person(van: VAN, requests_mock):
    json = delete_person_response
    # Test works with vanid
    requests_mock.delete(van.connection.uri + "people/19722445", json=json)
    response = van.delete_person("19722445")
    assert delete_person_response == response


def test_apply_canvass_result(van: VAN, requests_mock):
    # Test a valid attempt
    requests_mock.post(van.connection.uri + "people/2335282/canvassResponses", status_code=204)
    van.apply_canvass_result(2335282, 18)

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
    requests_mock.post(
        van.connection.uri + "people/2335282/canvassResponses",
        json=json,
        status_code=400,
    )
    with pytest.raises(HTTPError):
        van.apply_canvass_result(2335282, 0)

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
    requests_mock.post(
        van.connection.uri + "people/0/canvassResponses",
        json=json,
        status_code=400,
    )
    with pytest.raises(HTTPError):
        van.apply_canvass_result(0, 18)

    # Test a good dwid
    requests_mock.post(
        van.connection.uri + "people/DWID:2335282/canvassResponses",
        status_code=204,
    )
    van.apply_canvass_result(2335282, 18, id_type="DWID")

    # test canvassing via phone or sms without providing phone number
    with pytest.raises(HTTPError):
        van.apply_canvass_result(2335282, 18, contact_type_id=37)

    # test canvassing via phone or sms with providing phone number
    requests_mock.post(van.connection.uri + "people/2335282/canvassResponses", status_code=204)
    van.apply_canvass_result(2335282, 18, contact_type_id=37, phone="(516)-555-2342")


def test_apply_survey_question(van: VAN, requests_mock):
    # Test valid survey question
    requests_mock.post(van.connection.uri + "people/2335282/canvassResponses", status_code=204)
    van.apply_survey_response(2335282, 351006, 1443891)

    # Test bad survey response id
    # json = {
    #     'errors': [{
    #         'code': 'INVALID_PARAMETER',
    #         'text': ("'surveyResponseId' must be a valid Response to the given "
    #                  "Survey Question."),
    #         'properties': ['responses[0].surveyResponseId']
    #     }]
    # }
    requests_mock.post(van.connection.uri + "people/2335282/canvassResponses", status_code=400)
    with pytest.raises(HTTPError):
        van.apply_survey_response(2335282, 0, 1443891)

    # Test bad survey question id
    # json = {
    #     'errors': [{
    #         'code': 'INVALID_PARAMETER',
    #         'text': ("'surveyQuestionId' must be a valid Survey Question that is "
    #                 "available in the current context."),
    #         'properties': ['responses[0].surveyQuestionId']
    #     }]
    # }
    requests_mock.post(van.connection.uri + "people/2335282/canvassResponses", status_code=400)
    with pytest.raises(HTTPError):
        van.apply_survey_response(2335282, 351006, 0)


def test_toggle_volunteer_action():
    pass


def test_apply_response():
    pass


def test_create_relationship(van: VAN, requests_mock):
    relationship_id = 12
    bad_vanid_1 = 99999
    good_vanid_1 = 12345
    vanid_2 = 54321

    # Bad request
    requests_mock.post(
        van.connection.uri + f"people/{bad_vanid_1}/relationships",
        status_code=404,
    )

    # Good request
    requests_mock.post(
        van.connection.uri + f"people/{good_vanid_1}/relationships",
        status_code=204,
    )

    # Test bad input
    with pytest.raises(HTTPError):
        van.create_relationship(
            bad_vanid_1,
            vanid_2,
            relationship_id,
        )
    with pytest.raises(HTTPError):
        van.create_relationship(
            bad_vanid_1,
            vanid_2,
            relationship_id,
        )

    van.create_relationship(good_vanid_1, vanid_2, relationship_id)


def test_apply_person_code(van: VAN, requests_mock):
    vanid = 999
    code_id = 888

    # Test good request
    requests_mock.post(van.connection.uri + f"people/{vanid}/codes", status_code=204)
    van.apply_person_code(vanid, code_id)

    # Test bad request
    requests_mock.post(van.connection.uri + f"people/{vanid}/codes", status_code=404)
    with pytest.raises(HTTPError):
        van.apply_person_code(vanid, code_id)


def test_merge_contacts(van: VAN, requests_mock):
    source_vanid = 12345

    requests_mock.put(
        van.connection.uri + f"people/{source_vanid}/mergeInto",
        json=merge_contacts_response,
        status_code=200,
    )

    person = van.merge_contacts(source_vanid=source_vanid, primary_vanid=56789)

    assert person == merge_contacts_response
