import petl

from parsons import VAN, Table
from test.conftest import assert_matching_tables, validate_list


def test_get_targets(van: VAN, requests_mock):
    # Create response
    json = {
        "count": 2,
        "items": [
            {
                "targetId": 12827,
                "type": "TEST CODE",
                "name": "TEST CODE",
                "description": None,
                "points": 20,
                "areSubgroupsSticky": False,
                "status": "Active",
                "subgroups": None,
                "markedSubgroup": None,
            }
        ],
        "nextPageLink": None,
    }

    requests_mock.get(van.connection.uri + "targets", json=json)

    # Expected Structure
    expected = [
        "targetId",
        "type",
        "name",
        "description",
        "points",
        "areSubgroupsSticky",
        "status",
        "subgroups",
        "markedSubgroup",
    ]

    # Assert response is expected structure
    assert validate_list(expected, van.get_targets())

    # To Do: Test what happens when it doesn't find any targets


def test_get_target(van: VAN, requests_mock):
    # Create response
    json = {
        "targetId": 15723,
        "name": "Mail_VR_Chase",
        "type": "Dynamic",
        "description": None,
        "points": 15,
        "areSubgroupsSticky": False,
        "status": "Active",
        "subgroups": [
            {
                "targetId": 12827,
                "fullName": "April_VR_Chase Calls",
                "name": "April_Chase_20",
                "subgroupId": 46803,
                "isAssociatedWithBadges": True,
            }
        ],
        "markedSubgroup": None,
    }

    requests_mock.get(van.connection.uri + "targets/15723", json=json)

    assert json == van.get_target(15723)


def test_create_target_export(van: VAN, requests_mock):
    export_job_id = '{"exportJobId": "455961790"}'
    target_id = 12827

    requests_mock.post(
        van.connection.uri + "targetExportJobs",
        json=export_job_id,
        status_code=204,
    )

    # Test that it doesn't throw and error
    r = van.create_target_export(target_id, webhook_url=None)

    assert r == export_job_id


def test_get_target_export(van: VAN, requests_mock, mocker):
    fromcsv = mocker.patch.object(petl, "fromcsv", autospec=True)
    export_job_id = 455961790
    json = {
        "targetId": 12827,
        "file": {
            "downloadUrl": (
                "https://ngpvan.blob.core.windows.net/"
                "target-export-files/TargetExport_455961790.csv"
            ),
            "dateExpired": "null",
            "recordCount": 1016883,
        },
        "webhookUrl": "null",
        "exportJobId": 455961790,
        "jobStatus": "Complete",
    }

    download_url = (
        "https://ngpvan.blob.core.windows.net/target-export-files/TargetExport_455961790.csv"
    )
    fromcsv.return_value = petl.fromcolumns(
        [
            ["12827", "12827"],
            ["Volunteer Recruitment Tiers", "Volunteer Recruitment Tiers"],
            ["1111", "1111"],
            ["Tier", "Tier"],
            ["109957749", "109957754"],
        ],
        [
            "TargetID",
            "TargetName",
            "TargetSubgroupID",
            "TargetSubgroupName",
            "VanID",
        ],
    )

    requests_mock.post(
        van.connection.uri + "targetExportJobs",
        json=export_job_id,
        status_code=204,
    )
    requests_mock.get(van.connection.uri + "targetExportJobs/455961790", json=json)

    expected_result = Table(
        [
            (
                "TargetID",
                "TargetName",
                "TargetSubgroupID",
                "TargetSubgroupName",
                "VanID",
            ),
            ("12827", "Volunteer Recruitment Tiers", "1111", "Tier", "109957749"),
            ("12827", "Volunteer Recruitment Tiers", "1111", "Tier", "109957754"),
        ]
    )

    assert_matching_tables(van.get_target_export(export_job_id), expected_result)
    assert fromcsv.call_args == mocker.call(download_url, encoding="utf-8-sig")
