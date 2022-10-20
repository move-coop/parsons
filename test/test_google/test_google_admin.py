from parsons.etl.table import Table
from parsons.google.google_admin import GoogleAdmin
from test.utils import assert_matching_tables
from unittest.mock import MagicMock
import unittest


class MockGoogleAdmin(GoogleAdmin):
    def __init__(self):
        self.client = MagicMock()


class TestGoogleAdmin(unittest.TestCase):
    mock_aliases = Table([
        {'alias': 'fakeemail7@fakedomain.com'}, {'alias': 'fakeemail8@fakedomain.com'}
    ])
    mock_all_group_members = Table([
        {'email': 'fakeemail1@fakedomain.com'}, {'email': 'fakeemail2@fakedomain.com'},
        {'email': 'fakeemail3@fakedomain.com'}
    ])
    mock_all_groups = Table([
        {
            "aliases": ["fakeemail7@fakedomain.com", "fakeemail8@fakedomain.com"],
            'email': 'fakeemail4@fakedomain.com', 'id': 1
        },
        {'email': 'fakeemail5@fakedomain.com', 'id': 2},
        {'email': 'fakeemail6@fakedomain.com', 'id': 3}
    ])

    def setUp(self):
        self.google_admin = MockGoogleAdmin()

    def test_aliases(self):
        self.google_admin.client.request = MagicMock(return_value=(
            '',
            '{"aliases": [{"alias": "fakeemail7@fakedomain.com"},''{"alias": "fakeemail8@fakedomain'
            '.com"}]}'.encode()
        ))
        assert_matching_tables(self.google_admin.get_aliases('1'), self.mock_aliases)

    def test_all_group_members(self):
        self.google_admin.client.request = MagicMock(return_value=(
            '',
            '{"members": [{"email": "fakeemail1@fakedomain.com"}, {"email": '
            '"fakeemail2@fakedomain.com"}, {"email": "fakeemail3@fakedomain.com"}]}'.encode()
        ))
        assert_matching_tables(
            self.google_admin.get_all_group_members('group_key'), self.mock_all_group_members
        )

    def test_all_groups(self):
        self.google_admin.client.request = MagicMock(return_value=(
            '',
            '{"groups": [{"aliases": ["fakeemail7@fakedomain.com", "fakeemail8@fakedomain.com"], "e'
            'mail": "fakeemail4@fakedomain.com", "id": 1}, {"email": "fakeemail5@fakedomain.com", "'
            'id": 2}, {"email": "fakeemail6@fakedomain.com", "id": 3}]}'.encode()
        ))
        assert_matching_tables(
            self.google_admin.get_all_groups({'domain': 'fakedomain.com'}), self.mock_all_groups
        )
