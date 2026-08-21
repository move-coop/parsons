from parsons import VAN
from test.conftest import assert_matching_tables
from test.test_ngpvan.responses_people import get_person_response


def test_create_contact_note(van: VAN, requests_mock):
    requests_mock.post(van.connection.uri + "people/1/notes", status_code=204)
    van.create_contact_note(1, "a", True)


def test_get_contact_notes(van: VAN, requests_mock):
    json = get_person_response["notes"]
    requests_mock.get(van.connection.uri + "people/1/notes", json=json)
    assert_matching_tables(json, van.get_contact_notes("1"))
