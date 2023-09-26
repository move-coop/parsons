import unittest
import requests_mock
from parsons.mobilize_america import MobilizeAmerica
from test.utils import validate_list


class TestMobilizeAmerica(unittest.TestCase):

    def setUp(self):

        self.ma = MobilizeAmerica()

    def tearDown(self):

        pass

    def test_time_parse(self):

        # Test that Unix conversion works correctly
        self.assertEqual(self.ma._time_parse('<=2018-12-13'), 'lte_1544659200')

        # Test that it throws an error when you put in an invalid filter
        self.assertRaises(ValueError, self.ma._time_parse, '=2018-12-01')

    @requests_mock.Mocker()
    def test_get_organizations(self, m):

        json = {
            "count": 38,
            "next": None,
            "previous": (
                "https://events.mobilizeamerica.io/api/v1/organizations?updated_since=1543644000"),
            "data": [
                        {
                            "id": 1251,
                            "name": "Mike Blake for New York City",
                            "slug": "mikefornyc",
                            "is_coordinated": 'True',
                            "is_independent": 'True',
                            "is_primary_campaign": 'False',
                            "state": "",
                            "district": "",
                            "candidate_name": "",
                            "race_type": "OTHER_LOCAL",
                            "event_feed_url": "https://events.mobilizeamerica.io/mikefornyc/",
                            "created_date": 1545885434,
                            "modified_date": 1546132256
                        }
            ]
        }

        m.get(self.ma.uri + 'organizations', json=json)

        expected = [
            'id', 'name', 'slug', 'is_coordinated', 'is_independent', 'is_primary_campaign',
            'state', 'district', 'candidate_name', 'race_type', 'event_feed_url', 'created_date',
            'modified_date']

        # Assert response is expected structure
        self.assertTrue(validate_list(expected, self.ma.get_organizations()))

    @requests_mock.Mocker()
    def test_get_events(self, m):

        json = {
            'count': 1, 'next': None, 'previous': None,
            'data': [
                {
                    'id': 86738,
                    'description': (
                        'Join our team of volunteers and learn how to engage students in local '
                        'high schools, communicate our mission, and register young voters.'),
                    'timezone': 'America/Chicago',
                    'title': 'Student Voter Initiative Training',
                    'summary': '',
                    'featured_image_url': (
                        'https://mobilizeamerica.imgix.net/uploads/event/'
                        '40667432145_6188839fe3_o_20190102224312253645.jpeg'),
                    'sponsor': {
                        'id': 1076,
                        'name': 'Battleground Texas',
                        'slug': 'battlegroundtexas',
                        'is_coordinated': True,
                        'is_independent': False,
                        'is_primary_campaign': False,
                        'state': '',
                        'district': '',
                        'candidate_name': '',
                        'race_type': None,
                        'event_feed_url': 'https://events.mobilizeamerica.io/battlegroundtexas/',
                        'created_date': 1538590930,
                        'modified_date': 1546468308
                    },
                    'timeslots': [{
                        'id': 526226,
                        'start_date': 1547330400,
                        'end_date': 1547335800}],
                    'location': {
                        'venue': 'Harris County Democratic Party HQ',
                        'address_lines': ['4619 Lyons Ave', ''],
                        'locality': 'Houston',
                        'region': 'TX',
                        'postal_code': '77020',
                        'location': {'latitude': 29.776446, 'longitude': -95.323037},
                        'congressional_district': '18',
                        'state_leg_district': '142',
                        'state_senate_district': None
                    },
                    'event_type': 'TRAINING',
                    'created_date': 1546469706,
                    'modified_date': 1547335800,
                    'browser_url': (
                        'https://events.mobilizeamerica.io/battlegroundtexas/event/86738/'),
                    'high_priority': None,
                    'contact': None,
                    'visibility': 'PUBLIC'
                }
            ]
        }
        m.get(self.ma.uri + 'events', json=json)

        expected = [
            'id', 'description', 'timezone', 'title', 'summary', 'featured_image_url',
            'event_type', 'created_date', 'modified_date', 'browser_url', 'high_priority',
            'contact', 'visibility', 'sponsor_candidate_name', 'sponsor_created_date',
            'sponsor_district', 'sponsor_event_feed_url', 'sponsor_id', 'sponsor_is_coordinated',
            'sponsor_is_independent', 'sponsor_is_primary_campaign', 'sponsor_modified_date',
            'sponsor_name', 'sponsor_race_type', 'sponsor_slug', 'sponsor_state', 'address_lines',
            'congressional_district', 'locality', 'postal_code', 'region', 'state_leg_district',
            'state_senate_district', 'venue', 'latitude', 'longitude', 'timeslots_0_end_date',
            'timeslots_0_id', 'timeslots_0_start_date'
        ]

        # Assert response is expected structure
        self.assertTrue(validate_list(expected, self.ma.get_events()))

    @requests_mock.Mocker()
    def test_get_events_deleted(self, m):

        json = {'count': 2,
                'next': None,
                'previous': None,
                'data': [{'id': 86765,
                          'deleted_date': 1546705971},
                         {'id': 86782,
                          'deleted_date': 1546912779}
                         ]
                }

        m.get(self.ma.uri + 'events/deleted', json=json)

        # Assert response is expected structure
        self.assertTrue(validate_list(['id', 'deleted_date'], self.ma.get_events_deleted()))
