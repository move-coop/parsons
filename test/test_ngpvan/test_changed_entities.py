from parsons import VAN, Table
from test.conftest import assert_matching_tables


def test_get_changed_entity_resources(van: VAN, requests_mock):
    json = ["ActivistCodes", "ContactHistory", "Contacts", "ContactsActivistCodes"]
    requests_mock.get(van.connection.uri + "changedEntityExportJobs/resources", json=json)
    assert json == van.get_changed_entity_resources()


def test_get_changed_entity_resource_fields(van: VAN, requests_mock):
    json = [
        {
            "fieldName": "ActivistCodeID",
            "fieldType": "N",
            "maxTextboxCharacters": None,
            "isCoreField": True,
            "availableValues": None,
        },
        {
            "fieldName": "ActivistCodeType",
            "fieldType": "T",
            "maxTextboxCharacters": 20,
            "isCoreField": True,
            "availableValues": None,
        },
        {
            "fieldName": "Campaign",
            "fieldType": "T",
            "maxTextboxCharacters": 150,
            "isCoreField": True,
            "availableValues": None,
        },
    ]

    requests_mock.get(
        van.connection.uri + "changedEntityExportJobs/fields/ActivistCodes",
        json=json,
    )
    assert_matching_tables(Table(json), van.get_changed_entity_resource_fields("ActivistCodes"))


def test_get_changed_entities(van: VAN, requests_mock, mocker):
    json = {
        "dateChangedFrom": "2021-10-10T00:00:00-04:00",
        "dateChangedTo": "2021-10-11T00:00:00-04:00",
        "files": [],
        "message": "Created export job",
        "code": None,
        "exportedRecordCount": 0,
        "exportJobId": 2170181229,
        "jobStatus": "Pending",
    }

    json2 = {
        "dateChangedFrom": "2021-10-10T00:00:00-04:00",
        "dateChangedTo": "2021-10-11T00:00:00-04:00",
        "files": [
            {
                "downloadUrl": "https://box.com/file.csv",
                "dateExpired": "2021-11-03T15:27:01.8687339-04:00",
            }
        ],
        "message": "Finished processing export job",
        "code": None,
        "exportedRecordCount": 6110,
        "exportJobId": 2170181229,
        "jobStatus": "Complete",
    }

    tbl = Table([{"a": 1, "b": 2}])

    requests_mock.post(van.connection.uri + "changedEntityExportJobs", json=json)
    requests_mock.get(van.connection.uri + "changedEntityExportJobs/2170181229", json=json2)

    from_csv = mocker.patch.object(Table, "from_csv")
    from_csv.return_value = tbl

    out_tbl = van.get_changed_entities("ContactHistory", "2021-10-10")

    assert_matching_tables(out_tbl, tbl)
