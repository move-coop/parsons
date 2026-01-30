import unittest
from unittest.mock import MagicMock

from parsons.etl.table import Table
from parsons.google.google_admin import GoogleAdmin
from test.conftest import assert_matching_tables


class MockGoogleAdmin(GoogleAdmin):
    def __init__(self):
        self.client = MagicMock()


class TestGoogleAdmin(unittest.TestCase):
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

    def setUp(self):
        self.google_admin = MockGoogleAdmin()

    def test_aliases(self):
        response_mock = MagicMock()
        self.google_admin.client.request = MagicMock(return_value=response_mock)
        response_mock.json.return_value = {
            "aliases": [
                {"alias": "fakeemail7@fakedomain.com"},
                {"alias": "fakeemail8@fakedomain.com"},
            ]
        }
        assert_matching_tables(self.google_admin.get_aliases("1"), self.mock_aliases)

    def test_all_group_members(self):
        response_mock = MagicMock()
        self.google_admin.client.request = MagicMock(return_value=response_mock)
        response_mock.json.return_value = {"members": [{"email": "fakeemail4@fakedomain.com"}]}
        assert_matching_tables(
            self.google_admin.get_all_group_members("1"), self.mock_all_group_members
        )

    def test_all_groups(self):
        response_mock = MagicMock()
        self.google_admin.client.request = MagicMock(return_value=response_mock)
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
            self.google_admin.get_all_groups({"domain": "fakedomain.com"}),
            self.mock_all_groups,
        )
