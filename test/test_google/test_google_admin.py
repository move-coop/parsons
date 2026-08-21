from parsons.etl.table import Table
from test.conftest import assert_matching_tables

mock_aliases = Table(
    [{"alias": "fakeemail7@fakedomain.com"}, {"alias": "fakeemail8@fakedomain.com"}]
)
mock_all_group_members = Table([{"email": "fakeemail4@fakedomain.com"}])
mock_all_groups = Table(
    [
        {
            "aliases": ["fakeemail7@fakedomain.com", "fakeemail8@fakedomain.com"],
            "email": "fakeemail4@fakedomain.com",
            "id": 1,
        },
        {"aliases": None, "email": "fakeemail5@fakedomain.com", "id": 2},
        {"aliases": None, "email": "fakeemail6@fakedomain.com", "id": 3},
    ]
)


def test_aliases(google_admin, mocker):
    response_mock = mocker.MagicMock()
    google_admin.client.request = mocker.MagicMock(return_value=response_mock)
    response_mock.json.return_value = {
        "aliases": [
            {"alias": "fakeemail7@fakedomain.com"},
            {"alias": "fakeemail8@fakedomain.com"},
        ]
    }
    assert_matching_tables(google_admin.get_aliases("1"), mock_aliases)


def test_all_group_members(google_admin, mocker):
    response_mock = mocker.MagicMock()
    google_admin.client.request = mocker.MagicMock(return_value=response_mock)
    response_mock.json.return_value = {"members": [{"email": "fakeemail4@fakedomain.com"}]}
    assert_matching_tables(google_admin.get_all_group_members("1"), mock_all_group_members)


def test_all_groups(google_admin, mocker):
    response_mock = mocker.MagicMock()
    google_admin.client.request = mocker.MagicMock(return_value=response_mock)
    response_mock.json.return_value = {
        "groups": [
            {
                "aliases": [
                    "fakeemail7@fakedomain.com",
                    "fakeemail8@fakedomain.com",
                ],
                "email": "fakeemail4@fakedomain.com",
                "id": 1,
            },
            {"email": "fakeemail5@fakedomain.com", "id": 2},
            {"email": "fakeemail6@fakedomain.com", "id": 3},
        ]
    }
    assert_matching_tables(
        google_admin.get_all_groups({"domain": "fakedomain.com"}),
        mock_all_groups,
    )
