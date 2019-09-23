import unittest
import requests_mock
from test.utils import assert_matching_tables
from test.test_hustle import expected_json
from parsons import Table, Hustle
from parsons.hustle.hustle import HUSTLE_URI

CLIENT_ID = 'FAKE_ID'
CLIENT_SECRET = 'FAKE_SECRET'


class TestHustle(unittest.TestCase):

    @requests_mock.Mocker()
    def setUp(self, m):

        m.post(HUSTLE_URI + 'oauth/token', json=expected_json.auth_token)
        self.hustle = Hustle(CLIENT_ID, CLIENT_SECRET)

    @requests_mock.Mocker()
    def test_auth_token(self, m):

        self.assertEqual(self.hustle.auth_token, expected_json.auth_token['access_token'])

    @requests_mock.Mocker()
    def test_get_organizations(self, m):

        m.get(HUSTLE_URI + 'organizations', json=expected_json.organizations)
        orgs = self.hustle.get_organizations()
        assert_matching_tables(orgs, Table(expected_json.organizations['items']))

    @requests_mock.Mocker()
    def test_get_organization(self, m):

        m.get(HUSTLE_URI + 'organizations/LePEoKzD3', json=expected_json.organization)
        org = self.hustle.get_organization('LePEoKzD3')
        self.assertEqual(org, expected_json.organization)

    @requests_mock.Mocker()
    def test_get_groups(self, m):

        m.get(HUSTLE_URI + 'organizations/LePEoKzD3/groups', json=expected_json.groups)
        groups = self.hustle.get_groups('LePEoKzD3')
        assert_matching_tables(groups, Table(expected_json.groups['items']))

    @requests_mock.Mocker()
    def test_get_group(self, m):

        m.get(HUSTLE_URI + 'groups/zajXdqtzRt', json=expected_json.group)
        org = self.hustle.get_group('zajXdqtzRt')
        self.assertEqual(org, expected_json.group)

    @requests_mock.Mocker()
    def test_create_lead(self, m):

        m.post(HUSTLE_URI + 'groups/cMCH0hxwGt/leads', json=expected_json.lead)
        lead = self.hustle.create_lead('cMCH0hxwGt', 'Barack', '5126993336', last_name='Obama')
        self.assertEqual(lead, expected_json.lead)

    @requests_mock.Mocker()
    def test_create_leads(self, m):

        m.post(HUSTLE_URI + 'groups/cMCH0hxwGt/leads', json=expected_json.leads_tbl_01)

        tbl = Table([['phone_number', 'ln', 'first_name', 'address'],
                     ['4435705355', 'Johnson', 'Lyndon', '123 Main Street'],
                     ['4435705354', 'Richards', 'Ann', '124 Main Street']])
        self.hustle.create_leads(tbl, group_id='cMCH0hxwGt')

    @requests_mock.Mocker()
    def test_update_lead(self, m):

        m.put(HUSTLE_URI + 'leads/wqy78hlz2T', json=expected_json.updated_lead)
        updated_lead = self.hustle.update_lead('wqy78hlz2T', first_name='Bob')
        self.assertEqual(updated_lead, expected_json.updated_lead)

    @requests_mock.Mocker()
    def test_get_leads(self, m):

        # By Organization
        m.get(HUSTLE_URI + 'organizations/cMCH0hxwGt/leads', json=expected_json.leads)
        leads = self.hustle.get_leads(organization_id='cMCH0hxwGt')
        assert_matching_tables(leads, Table(expected_json.leads['items']))

        # By Group ID
        m.get(HUSTLE_URI + 'groups/cMCH0hxwGt/leads', json=expected_json.leads)
        leads = self.hustle.get_leads(group_id='cMCH0hxwGt')
        assert_matching_tables(leads, Table(expected_json.leads['items']))

    @requests_mock.Mocker()
    def test_get_lead(self, m):

        m.get(HUSTLE_URI + 'leads/wqy78hlz2T', json=expected_json.lead)
        lead = self.hustle.get_lead('wqy78hlz2T')
        self.assertEqual(lead, expected_json.lead)
