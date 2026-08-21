import pytest
from requests.exceptions import HTTPError

from parsons import VAN, Table
from test.conftest import assert_matching_tables, validate_list


def test_get_canvass_responses_contact_types(van: VAN, requests_mock):
    json = [{"name": "Auto Dial", "contactTypeId": 19, "channelTypeName": "Phone"}]

    requests_mock.get(van.connection.uri + "canvassResponses/contactTypes", json=json)

    assert_matching_tables(Table(json), van.get_canvass_responses_contact_types())


def test_get_canvass_responses_input_types(van: VAN, requests_mock):
    json = [{"inputTypeId": 11, "name": "API"}]
    requests_mock.get(van.connection.uri + "canvassResponses/inputTypes", json=json)
    assert_matching_tables(Table(json), van.get_canvass_responses_input_types())


def test_get_canvass_responses_result_codes(van: VAN, requests_mock):
    json = [
        {
            "shortName": "BZ",
            "resultCodeId": 18,
            "name": "Busy",
            "mediumName": "Busy",
        }
    ]

    requests_mock.get(van.connection.uri + "canvassResponses/resultCodes", json=json)
    assert_matching_tables(Table(json), van.get_canvass_responses_result_codes())


def test_get_survey_questions(van: VAN, requests_mock):
    json = {
        "count": 67,
        "items": [
            {
                "status": "Active",
                "responses": [
                    {
                        "shortName": "1",
                        "surveyResponseId": 1288926,
                        "name": "1-Strong Walz",
                        "mediumName": "1",
                    },
                    {
                        "shortName": "2",
                        "surveyResponseId": 1288928,
                        "name": "2-Lean Walz",
                        "mediumName": "2",
                    },
                ],
                "scriptQuestion": "Who do you support for Governor?",
                "name": "MN Governor Gen",
                "surveyQuestionId": 311838,
                "mediumName": "MNGovG",
                "shortName": "MGG",
                "type": "Candidate",
                "cycle": 2018,
            }
        ],
        "nextPageLink": None,
    }

    requests_mock.get(van.connection.uri + "surveyQuestions", json=json)

    expected = [
        "status",
        "responses",
        "scriptQuestion",
        "name",
        "surveyQuestionId",
        "mediumName",
        "shortName",
        "type",
        "cycle",
    ]

    assert validate_list(expected, van.get_survey_questions())


def test_get_supporter_groups(van: VAN, requests_mock):
    json = {
        "items": [
            {"id": 12, "name": "tmc", "description": "A fun group."},
            {"id": 13, "name": "tmc", "description": "A fun group."},
        ],
        "nextPageLink": None,
        "count": 3,
    }

    requests_mock.get(van.connection.uri + "supporterGroups", json=json)

    van.get_supporter_groups()


def test_get_supporter_group(van: VAN, requests_mock):
    json = [{"id": 12, "name": "tmc", "description": "A fun group."}]
    requests_mock.get(van.connection.uri + "supporterGroups/12", json=json)

    # Test that columns are expected columns
    assert van.get_supporter_group(12) == json


def test_delete_supporter_group(van: VAN, requests_mock):
    # Test good input
    good_supporter_group_id = 5
    good_ep = f"supporterGroups/{good_supporter_group_id}"
    requests_mock.delete(van.connection.uri + good_ep, status_code=204)
    van.delete_supporter_group(good_supporter_group_id)

    # Test bad input raises
    bad_supporter_group_id = 999
    # bad_vanid = 99999
    bad_ep = f"supporterGroups/{bad_supporter_group_id}"
    requests_mock.delete(van.connection.uri + bad_ep, status_code=404)
    with pytest.raises(HTTPError):
        van.delete_supporter_group(
            bad_supporter_group_id,
        )


def test_add_person_supporter_group(van: VAN, requests_mock):
    # Test good input
    good_supporter_group_id = 5
    good_vanid = 12345
    good_uri = f"supporterGroups/{good_vanid}/people/{good_supporter_group_id}"
    requests_mock.put(van.connection.uri + good_uri, status_code=204)
    van.add_person_supporter_group(good_vanid, good_supporter_group_id)

    # Test bad input
    bad_supporter_group_id = 999
    bad_vanid = 99999
    bad_uri = f"supporterGroups/{bad_vanid}/people/{bad_supporter_group_id}"
    requests_mock.put(van.connection.uri + bad_uri, status_code=404)
    with pytest.raises(HTTPError):
        van.add_person_supporter_group(
            bad_vanid,
            bad_supporter_group_id,
        )


def test_delete_person_supporter_group(van: VAN, requests_mock):
    # Test good input
    good_supporter_group_id = 5
    good_vanid = 12345
    good_ep = f"supporterGroups/{good_vanid}/people/{good_supporter_group_id}"
    requests_mock.delete(van.connection.uri + good_ep, status_code=204)
    van.delete_person_supporter_group(good_vanid, good_supporter_group_id)

    # Test bad input raises
    bad_supporter_group_id = 999
    bad_vanid = 99999
    bad_ep = f"supporterGroups/{bad_vanid}/people/{bad_supporter_group_id}"
    requests_mock.delete(van.connection.uri + bad_ep, status_code=404)
    with pytest.raises(HTTPError):
        van.delete_person_supporter_group(
            bad_vanid,
            bad_supporter_group_id,
        )
