import os
import unittest
import requests_mock
from test.utils import assert_matching_tables

from parsons.etl.table import Table
from parsons.zoom.zoom import Zoom


API_KEY = 'fake_api_key'
API_SECRET = 'fake_api_secret'
ZOOM_URI = 'https://api.zoom.us/v2/'


class TestZoom(unittest.TestCase):

    def setUp(self):

        self.zoom = Zoom(API_KEY, API_SECRET)

    @requests_mock.Mocker()
    def test_get_users(self, m):

      user_json = {
                   'page_count': 1,
                   'page_number': 1,
                   'page_size': 30,
                   'total_records': 1,
                   'users': [{
                      'id': 'C5A2nRWwTMm_hXyJb1JXMh',
                      'first_name': 'Bob',
                      'last_name': 'McBob',
                      'email': 'bob@bob.com',
                      'type': 2,
                      'pmi': 8374523641,
                      'timezone': 'America/New_York',
                      'verified': 1,
                      'dept': '',
                      'created_at': '2017-10-06T15:22:34Z',
                      'last_login_time': '2020-05-06T16:50:45Z',
                      'last_client_version': '',
                      'language': '',
                      'phone_number': '',
                      'status': 'active'}]}

      tbl = Table([{'id': 'C5A2nRWwTMm_hXyJb1JXMh',
                    'first_name': 'Bob',
                    'last_name': 'McBob',
                    'email': 'bob@bob.com',
                    'type': 2,
                    'pmi': 8374523641,
                    'timezone': 'America/New_York',
                    'verified': 1,
                    'dept': '',
                    'created_at': '2017-10-06T15:22:34Z',
                    'last_login_time': '2020-05-06T16:50:45Z',
                    'last_client_version': '',
                    'language': '',
                    'phone_number': '',
                    'status': 'active'}])

      m.get(ZOOM_URI + 'users', json=user_json)
      assert_matching_tables(self.zoom.get_users(), tbl)

    @requests_mock.Mocker()
    def test_get_meeting_participants(self, m):

      participants = {
                     'page_count': 1,
                     'page_size': 30,
                     'total_records': 4,
                     'next_page_token': '',
                     'participants': [{
                          'id': '',
                          'user_id': '16778240',
                          'name': 'Barack Obama',
                          'user_email': '',
                          'join_time': '2020-04-24T21:00:26Z',
                          'leave_time': '2020-04-24T22:24:38Z',
                          'duration': 5052,
                      'attentiveness_score': ''
                  }, {
                      'id': '',
                      'user_id': '16779264',
                      'name': '',
                      'user_email': '',
                      'join_time': '2020-04-24T21:00:45Z',
                      'leave_time': '2020-04-24T22:24:38Z',
                      'duration': 5033,
                      'attentiveness_score': ''
                  }]}

      tbl = Table([{
                   'id': '',
                   'user_id': '16778240',
                   'name': 'Barack Obama',
                   'user_email': '',
                   'join_time': '2020-04-24T21:00:26Z',
                   'leave_time': '2020-04-24T22:24:38Z',
                   'duration': 5052,
                   'attentiveness_score': ''
                    }, {
                   'id': '',
                   'user_id': '16779264',
                   'name': '',
                   'user_email': '',
                   'join_time': '2020-04-24T21:00:45Z',
                   'leave_time': '2020-04-24T22:24:38Z',
                   'duration': 5033,
                   'attentiveness_score': ''}])

      m.get(ZOOM_URI + '/report/meetings/123/participants', json=participants)
      assert_matching_tables(self.zoom.get_past_meeting_participants(123), tbl)