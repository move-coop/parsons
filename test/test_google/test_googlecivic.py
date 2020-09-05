import unittest
import requests_mock
from parsons.etl import Table
from parsons.google.google_civic import GoogleCivic
from googlecivic_responses import elections_resp, voterinfo_resp, polling_data
from test.utils import assert_matching_tables


class TestGoogleCivic(unittest.TestCase):

    def setUp(self):

        self.gc = GoogleCivic(api_key='FAKEKEY')

    @requests_mock.Mocker()
    def test_get_elections(self, m):

        m.get(self.gc.uri + 'elections', json=elections_resp)

        expected_tbl = Table(elections_resp['elections'])

        assert_matching_tables(self.gc.get_elections(), expected_tbl)

    @requests_mock.Mocker()
    def test_get_poll_location(self, m):

        m.get(self.gc.uri + 'voterinfo', json=voterinfo_resp)

        expected_tbl = Table(voterinfo_resp['pollingLocations'])

        tbl = self.gc.get_polling_location(2000, '900 N Washtenaw, Chicago, IL 60622')

        assert_matching_tables(tbl, expected_tbl)

    @requests_mock.Mocker()
    def test_get_poll_locations(self, m):

        m.get(self.gc.uri + 'voterinfo', json=voterinfo_resp)

        expected_tbl = Table(polling_data)

        address_tbl = Table([['address'],
                             ['900 N Washtenaw, Chicago, IL 60622'],
                             ['900 N Washtenaw, Chicago, IL 60622']])

        tbl = self.gc.get_polling_locations(2000, address_tbl)

        assert_matching_tables(tbl, expected_tbl)
