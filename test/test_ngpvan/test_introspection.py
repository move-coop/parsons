from parsons import VAN


def test_get_apikeyprofiles(van: VAN, requests_mock):
    json = {
        "items": [
            {
                "databaseName": "SmartVAN Massachusetts",
                "hasMyVoters": True,
                "hasMyCampaign": True,
                "committeeName": "People for Good",
                "apiKeyTypeName": "Custom Integration",
                "keyReference": "1234",
                "userFirstName": "peopleforgood",
                "userLastName": "api",
                "username": "peopleforgood.api",
                "userId": 4321,
            }
        ],
        "nextPageLink": None,
        "count": 1,
    }

    requests_mock.get(van.connection.uri + "apiKeyProfiles", json=json)

    # # Call the method that makes the API request
    response = van.get_apikeyprofiles()

    # Assert that the response is a dictionary (JSON object)
    assert isinstance(response, dict)

    # Assert that the response matches the expected JSON
    # I have to access a part of the json because the response is a list of dictionaries
    # and the VAN Connector handles the pagination and unpacks the list of dictionaries
    assert response == json["items"][0]
