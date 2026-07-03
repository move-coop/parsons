from parsons import VAN
from test.conftest import validate_list


def test_get_activist_codes(van: VAN, requests_mock):
    # Create response
    json = {
        "count": 43,
        "items": [
            {
                "status": "Active",
                "scriptQuestion": None,
                "name": "TEST CODE",
                "mediumName": "TEST CODE",
                "activistCodeId": 4388538,
                "shortName": "TC",
                "type": "Action",
                "description": None,
            }
        ],
        "nextPageLink": None,
    }

    requests_mock.get(van.connection.uri + "activistCodes", json=json)

    # Expected Structure
    expected = [
        "status",
        "scriptQuestion",
        "name",
        "mediumName",
        "activistCodeId",
        "shortName",
        "type",
        "description",
    ]

    # Assert response is expected structure
    assert validate_list(expected, van.get_activist_codes())

    # To Do: Test what happens when it doesn't find any ACs


def test_get_activist_code(van: VAN, requests_mock):
    # Create response
    json = {
        "status": "Active",
        "scriptQuestion": "null",
        "name": "Anti-Choice",
        "mediumName": "Anti",
        "activistCodeId": 4135099,
        "shortName": "AC",
        "type": "Constituency",
        "description": "A person who has been flagged as anti-choice.",
    }

    requests_mock.get(van.connection.uri + "activistCodes/4388538", json=json)

    assert json == van.get_activist_code(4388538)


def test_toggle_activist_code(van: VAN, requests_mock):
    # Test apply activist code
    requests_mock.post(van.connection.uri + "people/2335282/canvassResponses", status_code=204)
    assert van.toggle_activist_code(2335282, 4429154, "apply"), 204

    # Test remove activist code
    requests_mock.post(van.connection.uri + "people/2335282/canvassResponses", status_code=204)
    assert van.toggle_activist_code(2335282, 4429154, "remove"), 204


def test_apply_activist_code(van: VAN, requests_mock):
    # Test apply activist code
    requests_mock.post(van.connection.uri + "people/2335282/canvassResponses", status_code=204)
    assert van.apply_activist_code(2335282, 4429154) == 204


def test_remove_activist_code(van: VAN, requests_mock):
    # Test remove activist code
    requests_mock.post(van.connection.uri + "people/2335282/canvassResponses", status_code=204)
    assert van.remove_activist_code(2335282, 4429154) == 204
