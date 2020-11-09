import unittest
import requests_mock
import json
from parsons import Table, ActionNetwork
from test.utils import assert_matching_tables


class TestActionNetwork(unittest.TestCase):

    @requests_mock.Mocker()
    def setUp(self, m):

        self.api_url = 'https://actionnetwork.org/api/v2'
        self.api_key = "fake_key"

        self.an = ActionNetwork(self.api_key)

        self.fake_datetime = '2019-02-29T00:00:00.000+0000'
        self.fake_date = '2019-02-29'
        self.fake_customer_email_1 = 'fake_customer_email_1@fake_customer_email.com'
        self.fake_customer_email_2 = 'fake_customer_email_2@fake_customer_email.com'
        self.fake_person_id_1 = "fake_person_id_1"
        self.fake_person_id_2 = "fake_person_id_2"
        self.fake_tag_id_1 = "fake_tag_id_1"
        self.fake_tag_id_2 = "fake_tag_id_2"
        self.fake_people_list_1 = {
         'per_page': 2,
         'page': 1,
         '_links': {'next': {'href': f"{self.api_url}/people?page=2"},
                    'osdi:people': [{'href': f"{self.api_url}/{self.fake_person_id_1}"},
                                    {'href': f"{self.api_url}/{self.fake_person_id_2}"}],
                    'curies': [{'name': 'osdi',
                                'templated': True},
                               {'name': 'action_network',
                                'templated': True}],
                    'self': {'href': f"{self.api_url}/people"}},
         '_embedded': {'osdi:people': [{'given_name': 'Fakey',
                                        'family_name': 'McFakerson',
                                        'identifiers': [self.fake_person_id_1],
                                        'email_addresses': [{'primary': True,
                                                             'address': self.fake_customer_email_1,
                                                             'status': 'subscribed'}],
                                        'postal_addresses': [{'primary': True,
                                                              'region': '',
                                                              'country': 'US',
                                                              'location': {'latitude': None,
                                                                           'longitude': None,
                                                                           'accuracy': None}}],
                                        'created_date': self.fake_datetime,
                                        'modified_date': self.fake_datetime,
                                        'languages_spoken': ['en']},
                                       {'given_name': 'Faker',
                                        'family_name': 'McEvenFakerson',
                                        'identifiers': [self.fake_person_id_2],
                                        'email_addresses': [{'primary': True,
                                                             'address': self.fake_customer_email_2,
                                                             'status': 'subscribed'}],
                                        'postal_addresses': [{'primary': True,
                                                              'region': '',
                                                              'country': 'US',
                                                              'location': {'latitude': None,
                                                                           'longitude': None,
                                                                           'accuracy': None}}],
                                        'created_date': self.fake_datetime,
                                        'modified_date': self.fake_datetime,
                                        'languages_spoken': ['en']}]}}
        self.fake_people_list_2 = {
         'per_page': 2,
         'page': 2,
         '_links': {'next': {'href': f"{self.api_url}/people?page=3"},
                    'osdi:people': [{'href': f"{self.api_url}/{self.fake_person_id_1}"},
                                    {'href': f"{self.api_url}/{self.fake_person_id_2}"}],
                    'curies': [{'name': 'osdi',
                                'templated': True},
                               {'name': 'action_network',
                                'templated': True}],
                    'self': {'href': f"{self.api_url}/people"}},
         '_embedded': {'osdi:people': [{'given_name': 'Fakey',
                                        'family_name': 'McFakerson',
                                        'identifiers': [self.fake_person_id_1],
                                        'email_addresses': [{'primary': True,
                                                             'address': self.fake_customer_email_1,
                                                             'status': 'subscribed'}],
                                        'postal_addresses': [{'primary': True,
                                                              'region': '',
                                                              'country': 'US',
                                                              'location': {'latitude': None,
                                                                           'longitude': None,
                                                                           'accuracy': None}}],
                                        'created_date': self.fake_datetime,
                                        'modified_date': self.fake_datetime,
                                        'languages_spoken': ['en']},
                                       {'given_name': 'Faker',
                                        'family_name': 'McEvenFakerson',
                                        'identifiers': [self.fake_person_id_2],
                                        'email_addresses': [{'primary': True,
                                                             'address': self.fake_customer_email_2,
                                                             'status': 'subscribed'}],
                                        'postal_addresses': [{'primary': True,
                                                              'region': '',
                                                              'country': 'US',
                                                              'location': {'latitude': None,
                                                                           'longitude': None,
                                                                           'accuracy': None}}],
                                        'created_date': self.fake_datetime,
                                        'modified_date': self.fake_datetime,
                                        'languages_spoken': ['en']}]}}
        self.fake_people_list = (self.fake_people_list_1['_embedded']['osdi:people'] +
                                 self.fake_people_list_2['_embedded']['osdi:people'])
        self.fake_tag_list = {
         'total_pages': 1,
         'per_page': 2,
         'page': 1,
         'total_records': 2,
         '_links': {'next': {'href': f"{self.api_url}/tags?page=2"},
                    'osdi:tags': [{'href': f"{self.api_url}/tags/{self.fake_tag_id_1}"},
                                  {'href': f"{self.api_url}/tags/{self.fake_tag_id_2}"}],
                    'curies': [{'name': 'osdi',
                                'templated': True},
                               {'name': 'action_network',
                                'templated': True}],
                    'self': {'href': f"{self.api_url}/tags"}},
         '_embedded': {'osdi:tags': [{'name': "fake_tag_1",
                                      'created_date': self.fake_datetime,
                                      'modified_date': self.fake_datetime,
                                      'identifiers': [self.fake_tag_id_1],
                                      '_links':
                                      {'self': {'href': self.fake_tag_id_1}}},
                                     {'name': "fake_tag_2",
                                      'created_date': self.fake_datetime,
                                      'modified_date': self.fake_datetime,
                                      'identifiers': [self.fake_tag_id_1],
                                      '_links': {'self': {'href': self.fake_tag_id_1}}}]}}
        self.fake_person = [
               {'given_name': 'Fakey',
                'family_name': 'McFakerson',
                'identifiers': [self.fake_person_id_1],
                'email_addresses': [{'primary': True,
                                     'address': 'fakey@mcfakerson.com',
                                     'status': 'unsubscribed'}],
                'postal_addresses': [{'primary': True,
                                      'locality': 'Washington',
                                      'region': 'DC',
                                      'postal_code': '20009',
                                      'country': 'US',
                                      'location': {'latitude': 38.919,
                                                   'longitude': -77.0378,
                                                   'accuracy': None}}],
                '_links': {'self': {'href': 'fake_url'},
                           'osdi:signatures': {'href': 'fake_url'},
                           'osdi:submissions': {'href': 'fake_url'},
                           'osdi:donations': {'href': 'fake_url'},
                           'curies': [{'name': 'osdi',
                                       'href': 'fake_url',
                                       'templated': True},
                                      {'name': 'action_network',
                                       'href': 'fake_url',
                                       'templated': True}],
                           'osdi:taggings': {'href': 'fake_url'},
                           'osdi:outreaches': {'href': 'fake_url'},
                           'osdi:attendances': {'href': 'fake_url'}},
                'custom_fields': {},
                'created_date': self.fake_date,
                'modified_date': self.fake_date,
                'languages_spoken': ['en']}]
        self.updated_fake_person = [
         {'given_name': 'Flakey',
          'family_name': 'McFlakerson',
          'identifiers': [self.fake_person_id_1],
          'email_addresses': [{'primary': True,
                               'address': 'fakey@mcfakerson.com',
                               'status': 'unsubscribed'}],
          'postal_addresses': [{'primary': True,
                                'locality': 'Washington',
                                'region': 'DC',
                                'postal_code': '20009',
                                'country': 'US',
                                'location': {'latitude': 38.919,
                                             'longitude': -77.0378,
                                             'accuracy': None}}],
          '_links': {'self': {'href': 'fake_url'},
                     'osdi:signatures': {'href': 'fake_url'},
                     'osdi:submissions': {'href': 'fake_url'},
                     'osdi:donations': {'href': 'fake_url'},
                     'curies': [{'name': 'osdi',
                                 'href': 'fake_url',
                                 'templated': True},
                                {'name': 'action_network',
                                 'href': 'fake_url',
                                 'templated': True}],
                     'osdi:taggings': {'href': 'fake_url'},
                     'osdi:outreaches': {'href': 'fake_url'},
                     'osdi:attendances': {'href': 'fake_url'}},
          'custom_fields': {},
          'created_date': self.fake_date,
          'modified_date': self.fake_date,
          'languages_spoken': ['en']}]
        self.fake_tag = {'name': "fake_tag_1",
                         'created_date': self.fake_datetime,
                         'modified_date': self.fake_datetime,
                         'identifiers': [self.fake_tag_id_1],
                         '_links': {'self': {'href': self.fake_tag_id_1}}}

    @requests_mock.Mocker()
    def test_get_page(self, m):
        m.get(f"{self.api_url}/people?page=2&per_page=2", text=json.dumps(self.fake_people_list_2))
        self.assertEqual(self.an._get_page('people', 2, 2), self.fake_people_list_2)

    @requests_mock.Mocker()
    def test_get_entry_list(self, m):
        m.get(f"{self.api_url}/people?page=1&per_page=25", text=json.dumps(self.fake_people_list_1))
        m.get(f"{self.api_url}/people?page=2&per_page=25", text=json.dumps(self.fake_people_list_2))
        m.get(f"{self.api_url}/people?page=3&per_page=25",
              text=json.dumps({'_embedded': {"osdi:people": []}}))
        assert_matching_tables(self.an._get_entry_list('people'),
                               Table(self.fake_people_list))

    @requests_mock.Mocker()
    def test_get_people(self, m):
        m.get(f"{self.api_url}/people?page=1&per_page=25", text=json.dumps(self.fake_people_list_1))
        m.get(f"{self.api_url}/people?page=2&per_page=25", text=json.dumps(self.fake_people_list_2))
        m.get(f"{self.api_url}/people?page=3&per_page=25",
              text=json.dumps({'_embedded': {"osdi:people": []}}))
        assert_matching_tables(self.an.get_people(), Table(self.fake_people_list))

    @requests_mock.Mocker()
    def test_get_tags(self, m):
        m.get(f"{self.api_url}/tags?page=1&per_page=25", text=json.dumps(self.fake_tag_list))
        m.get(f"{self.api_url}/tags?page=2&per_page=25",
              text=json.dumps({'_embedded': {"osdi:tags": []}}))
        assert_matching_tables(self.an.get_tags(),
                               Table(self.fake_tag_list['_embedded']['osdi:tags']))

    @requests_mock.Mocker()
    def test_get_person(self, m):
        m.get(f"{self.api_url}/people/{self.fake_person_id_1}", text=json.dumps(self.fake_person))
        self.assertEqual(self.an.get_person(self.fake_person_id_1), self.fake_person)

    @requests_mock.Mocker()
    def test_get_tag(self, m):
        m.get(f"{self.api_url}/tags/{self.fake_tag_id_1}", text=json.dumps(self.fake_tag))
        self.assertEqual(self.an.get_tag(self.fake_tag_id_1), self.fake_tag)

    @requests_mock.Mocker()
    def test_update_person(self, m):
        m.put(f"{self.api_url}/people/{self.fake_person_id_1}",
              text=json.dumps(self.updated_fake_person))
        self.assertEqual(self.an.update_person(self.fake_person_id_1,
                                               given_name='Flake',
                                               family_name='McFlakerson'),
                         self.updated_fake_person)
