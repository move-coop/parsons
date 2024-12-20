import unittest
from test.utils import assert_matching_tables

import requests_mock
from parsons import Table, NewmodeV2

CLIENT_ID = "fakeClientID"
CLIENT_SECRET = "fakeClientSecret"


API_URL = "https://base.newmode.net/api/"
API_AUTH_URL = "https://base.newmode.net/oauth/token/"
API_CAMPAIGNS_URL = "https://base.newmode.net/"


class TestZoom(unittest.TestCase):
    @requests_mock.Mocker()
    def setUp(self, m):
        m.post(API_AUTH_URL, json={"access_token": "fakeAccessToken"})
        self.nm = NewmodeV2(CLIENT_ID, CLIENT_SECRET)

    @requests_mock.Mocker()
    def test_get_campaign(self, m):
        campaign_id= "fakeCampaignID"
        result={'contact': {'id': [{'value': 26237005}], 'uuid': [{'value': 'b897e271-94ef-4e21-96eb-08919c3cf96a'}], 'revision_id': [{'value': 307400}], 'org_id': [{'value': 2125}], 'honorific': [], 'first_name': [{'value': 'TestFirstName'}], 'last_name': [{'value': 'TestLastName'}], 'name_suffix': [], 'email': [{'value': 'test_abc@test.com'}], 'mobile_phone': [], 'alternate_phone': [], 'twitter_handle': [], 'street_address': [], 'city': [], 'region': [], 'country': [], 'postal_code': [{'value': 'V6A 2T2'}], 'latitude': [], 'longitude': [], 'opt_in': [{'value': True}], 'nm_product_opt_in': [{'value': False}], 'nm_marketing_opt_in': [{'value': False}], 'groups': [{'target_id': 1189, 'target_type': 'contact_group', 'target_uuid': '0ad63afe-703c-4df3-8c4f-b2fe2183497b', 'url': '/contact-group/1189'}], 'created': [{'value': '1734674126', 'format': 'Y-m-d\\TH:i:sP'}], 'changed': [{'value': '1734674126', 'format': 'Y-m-d\\TH:i:sP'}], 'prefill_hash': [{'value': '90dfa191e412370e911554ab36d010e98527e0f058ea9d6f4affad5ebd6bd328'}], 'subscriber': [], 'sync_status': [[]], 'entitygroupfield': [{'target_id': 2664911, 'target_type': 'group_content', 'target_uuid': '95631305-d57a-467a-af88-d549daf471fe', 'url': '/group/2125/content/2664911'}]}, 'links': {'Facebook': {'label': 'Share on Facebook', 'url': 'https://www.facebook.com/sharer.php?s=100&u=https://win.newmode.net/themovementcooperative/teset', 'title': ''}, 'Twitter': {'label': 'Tweet to your followers', 'url': 'https://nwmd.social/s/twitter/5AuGY1uWfuXNxLKMmQ==/b', 'title': ''}, 'Email': {'label': 'Send an email', 'url': 'https://nwmd.social/s/email/5AuGY1uWfuXNxLKMmQ==/b', 'title': 'Add your voice to this campaign!'}, 'Copy Link': {'label': 'Copy Link', 'url': 'https://nwmd.social/s/copylink/5AuGY1uWfuXNxLKMmQ==/b', 'title': ''}}, 'message': 'Already submitted', 'submission': {'sid': [{'value': 346473}], 'uuid': [{'value': 'a712fb0f-f19f-4455-8585-f3dd95415be1'}], 'revision_id': [{'value': 346473}], 'action_id': [{'target_id': 5003, 'target_type': 'node', 'target_uuid': 'd848035a-f7fd-468a-a977-40b46d7a97b9', 'url': '/node/5003'}], 'contact_id': [{'target_id': 26237005, 'target_type': 'contact', 'target_uuid': 'b897e271-94ef-4e21-96eb-08919c3cf96a', 'url': '/contact/26237005'}], 'status': [{'target_id': 78, 'target_type': 'taxonomy_term', 'target_uuid': '1b680fc7-3a53-4790-8865-888e0f5bba19', 'url': '/taxonomy/term/78'}], 'testmode': [{'value': False}], 'edited': [{'value': True}], 'device': [], 'browser': [], 'browser_version': [], 'os': [], 'os_version': [], 'parent_url': [], 'source_code': [], 'search_value': [], 'created': [{'value': '1734674126', 'format': 'Y-m-d\\TH:i:sP'}], 'changed': [{'value': '1734674126', 'format': 'Y-m-d\\TH:i:sP'}], 'entitygroupfield': [{'target_id': 2664913, 'target_type': 'group_content', 'target_uuid': 'fb99d1d0-a329-4354-9f8d-9b236e751714', 'url': '/group/2125/content/2664913'}]}, 'ref_id': '90dfa191e412370e911554ab36d010e98527e0f058ea9d6f4affad5ebd6bd328'}
        tbl = Table(
            [
                {
                    "id": "C5A2nRWwTMm_hXyJb1JXMh",
                    "first_name": "Bob",
                    "last_name": "McBob",
                    "email": "bob@bob.com",
                    "type": 2,
                    "pmi": 8374523641,
                    "timezone": "America/New_York",
                    "verified": 1,
                    "dept": "",
                    "created_at": "2017-10-06T15:22:34Z",
                    "last_login_time": "2020-05-06T16:50:45Z",
                    "last_client_version": "",
                    "language": "",
                    "phone_number": "",
                    "status": "active",
                }
            ]
        )

        m.post(API_AUTH_URL, json={"access_token": "fakeAccessToken"})
        m.get(API_URL + "users", json=user_json)
        assert_matching_tables(self.zoom.get_users(), tbl)

    @requests_mock.Mocker()
    def test_get_meeting_participants(self, m):
        participants = {
            "page_count": 1,
            "page_size": 30,
            "total_records": 4,
            "next_page_token": "",
            "participants": [
                {
                    "id": "",
                    "user_id": "16778240",
                    "name": "Barack Obama",
                    "user_email": "",
                    "join_time": "2020-04-24T21:00:26Z",
                    "leave_time": "2020-04-24T22:24:38Z",
                    "duration": 5052,
                    "attentiveness_score": "",
                },
                {
                    "id": "",
                    "user_id": "16779264",
                    "name": "",
                    "user_email": "",
                    "join_time": "2020-04-24T21:00:45Z",
                    "leave_time": "2020-04-24T22:24:38Z",
                    "duration": 5033,
                    "attentiveness_score": "",
                },
            ],
        }

        tbl = Table(
            [
                {
                    "id": "",
                    "user_id": "16778240",
                    "name": "Barack Obama",
                    "user_email": "",
                    "join_time": "2020-04-24T21:00:26Z",
                    "leave_time": "2020-04-24T22:24:38Z",
                    "duration": 5052,
                    "attentiveness_score": "",
                },
                {
                    "id": "",
                    "user_id": "16779264",
                    "name": "",
                    "user_email": "",
                    "join_time": "2020-04-24T21:00:45Z",
                    "leave_time": "2020-04-24T22:24:38Z",
                    "duration": 5033,
                    "attentiveness_score": "",
                },
            ]
        )

        m.post(API_AUTH_URL, json={"access_token": "fakeAccessToken"})
        m.get(API_URL + "report/meetings/123/participants", json=participants)
        assert_matching_tables(self.zoom.get_past_meeting_participants(123), tbl)

    @requests_mock.Mocker()
    def test_get_meeting_registrants(self, m):
        registrants = {
            "page_count": 1,
            "page_size": 30,
            "total_records": 4,
            "next_page_token": "",
            "registrants": [
                {
                    "id": "",
                    "user_id": "16778240",
                    "name": "Barack Obama",
                    "user_email": "",
                    "purchasing_time_frame": "Within a month",
                    "role_in_purchase_process": "Not involved",
                },
                {
                    "id": "",
                    "user_id": "16779264",
                    "name": "",
                    "user_email": "",
                    "purchasing_time_frame": "Within a month",
                    "role_in_purchase_process": "Not involved",
                },
            ],
        }

        tbl = Table(
            [
                {
                    "id": "",
                    "user_id": "16778240",
                    "name": "Barack Obama",
                    "user_email": "",
                    "purchasing_time_frame": "Within a month",
                    "role_in_purchase_process": "Not involved",
                },
                {
                    "id": "",
                    "user_id": "16779264",
                    "name": "",
                    "user_email": "",
                    "purchasing_time_frame": "Within a month",
                    "role_in_purchase_process": "Not involved",
                },
            ]
        )

        m.post(API_AUTH_URL, json={"access_token": "fakeAccessToken"})
        m.get(API_URL + "meetings/123/registrants", json=registrants)
        assert_matching_tables(self.zoom.get_meeting_registrants(123), tbl)

    @requests_mock.Mocker()
    def test_get_user_webinars(self, m):
        webinars = {
            "page_count": 1,
            "page_size": 30,
            "total_records": 4,
            "next_page_token": "",
            "webinars": [
                {
                    "uuid": "dsghfkhaewfds",
                    "id": "",
                    "host_id": "24654130000000",
                    "topic": "My Webinar",
                    "agenda": "Learn more about Zoom APIs",
                    "type": "5",
                    "duration": "60",
                    "start_time": "2019-09-24T22:00:00Z",
                    "timezone": "America/Los_Angeles",
                    "created_at": "2019-08-30T22:00:00Z",
                    "join_url": "https://zoom.us/0001000/awesomewebinar",
                },
                {
                    "uuid": "dhf8as7dhf",
                    "id": "",
                    "host_id": "24654130000345",
                    "topic": "My Webinar",
                    "agenda": "Learn more about Zoom APIs",
                    "type": "5",
                    "duration": "60",
                    "start_time": "2019-09-24T22:00:00Z",
                    "timezone": "America/Los_Angeles",
                    "created_at": "2019-08-30T22:00:00Z",
                    "join_url": "https://zoom.us/0001000/awesomewebinar",
                },
            ],
        }

        tbl = Table(
            [
                {
                    "uuid": "dsghfkhaewfds",
                    "id": "",
                    "host_id": "24654130000000",
                    "topic": "My Webinar",
                    "agenda": "Learn more about Zoom APIs",
                    "type": "5",
                    "duration": "60",
                    "start_time": "2019-09-24T22:00:00Z",
                    "timezone": "America/Los_Angeles",
                    "created_at": "2019-08-30T22:00:00Z",
                    "join_url": "https://zoom.us/0001000/awesomewebinar",
                },
                {
                    "uuid": "dhf8as7dhf",
                    "id": "",
                    "host_id": "24654130000345",
                    "topic": "My Webinar",
                    "agenda": "Learn more about Zoom APIs",
                    "type": "5",
                    "duration": "60",
                    "start_time": "2019-09-24T22:00:00Z",
                    "timezone": "America/Los_Angeles",
                    "created_at": "2019-08-30T22:00:00Z",
                    "join_url": "https://zoom.us/0001000/awesomewebinar",
                },
            ]
        )

        m.post(API_AUTH_URL, json={"access_token": "fakeAccessToken"})
        m.get(API_URL + "users/123/webinars", json=webinars)
        assert_matching_tables(self.zoom.get_user_webinars(123), tbl)

    @requests_mock.Mocker()
    def test_get_past_webinar_participants(self, m):
        participants = {
            "page_count": 1,
            "page_size": 30,
            "total_records": 4,
            "next_page_token": "",
            "participants": [
                {
                    "id": "",
                    "user_id": "sdfjkldsf87987",
                    "name": "Barack",
                    "user_email": "riya@sdfjkldsf87987.fdjfhdf",
                    "join_time": "2019-02-01T12:34:12.660Z",
                    "leave_time": "2019-03-01T12:34:12.660Z",
                    "duration": "20",
                },
                {
                    "id": "",
                    "user_id": "sdfjkldsfdfgdfg",
                    "name": "Joe",
                    "user_email": "riya@sdfjkldsf87987.fdjfhdf",
                    "join_time": "2019-02-01T12:34:12.660Z",
                    "leave_time": "2019-03-01T12:34:12.660Z",
                    "duration": "20",
                },
            ],
        }

        tbl = Table(
            [
                {
                    "id": "",
                    "user_id": "sdfjkldsf87987",
                    "name": "Barack",
                    "user_email": "riya@sdfjkldsf87987.fdjfhdf",
                    "join_time": "2019-02-01T12:34:12.660Z",
                    "leave_time": "2019-03-01T12:34:12.660Z",
                    "duration": "20",
                },
                {
                    "id": "",
                    "user_id": "sdfjkldsfdfgdfg",
                    "name": "Joe",
                    "user_email": "riya@sdfjkldsf87987.fdjfhdf",
                    "join_time": "2019-02-01T12:34:12.660Z",
                    "leave_time": "2019-03-01T12:34:12.660Z",
                    "duration": "20",
                },
            ]
        )

        m.post(API_AUTH_URL, json={"access_token": "fakeAccessToken"})
        m.get(API_URL + "report/webinars/123/participants", json=participants)
        assert_matching_tables(self.zoom.get_past_webinar_participants(123), tbl)

    @requests_mock.Mocker()
    def test_get_past_webinar_report(self, m):
        report = {
            "custom_keys": [{"key": "Host Nation", "value": "US"}],
            "dept": "HR",
            "duration": 2,
            "end_time": "2022-03-15T07:42:22Z",
            "id": 345678902224,
            "participants_count": 4,
            "start_time": "2022-03-15T07:40:46Z",
            "topic": "My Meeting",
            "total_minutes": 3,
            "tracking_fields": [{"field": "Host Nation", "value": "US"}],
            "type": 4,
            "user_email": "jchill@example.com",
            "user_name": "Jill Chill",
            "uuid": "4444AAAiAAAAAiAiAiiAii==",
        }

        m.post(API_AUTH_URL, json={"access_token": "fakeAccessToken"})
        m.get(API_URL + "report/webinars/123", json=report)
        assert_matching_tables(self.zoom.get_past_webinar_report(123), report)

    @requests_mock.Mocker()
    def test_get_webinar_registrants(self, m):
        registrants = {
            "page_count": 1,
            "page_size": 30,
            "total_records": 4,
            "next_page_token": "",
            "registrants": [
                {
                    "id": "",
                    "email": "barack@obama.com",
                    "first_name": "Barack",
                    "last_name": "Obama",
                    "address": "dsfhkdjsfh st",
                    "city": "jackson heights",
                    "country": "US",
                    "zip": "11371",
                    "state": "NY",
                    "phone": "00000000",
                    "industry": "Food",
                    "org": "Cooking Org",
                    "job_title": "Chef",
                    "purchasing_time_frame": "1-3 months",
                    "role_in_purchase_process": "Influencer",
                    "no_of_employees": "10",
                    "comments": "Looking forward to the Webinar",
                    "custom_questions": [
                        {
                            "title": "What do you hope to learn from this Webinar?",
                            "value": "Look forward to learning how you come up with recipes and services",  # noqa: E501
                        }
                    ],
                    "status": "approved",
                    "create_time": "2019-02-26T23:01:16.899Z",
                    "join_url": "https://zoom.us/webinar/mywebinariscool",
                },
                {
                    "id": "",
                    "email": "joe@biden.com",
                    "first_name": "Joe",
                    "last_name": "Biden",
                    "address": "dsfhkdjsfh st",
                    "city": "jackson heights",
                    "country": "US",
                    "zip": "11371",
                    "state": "NY",
                    "phone": "00000000",
                    "industry": "Food",
                    "org": "Cooking Org",
                    "job_title": "Chef",
                    "purchasing_time_frame": "1-3 months",
                    "role_in_purchase_process": "Influencer",
                    "no_of_employees": "10",
                    "comments": "Looking forward to the Webinar",
                    "custom_questions": [
                        {
                            "title": "What do you hope to learn from this Webinar?",
                            "value": "Look forward to learning how you come up with recipes and services",  # noqa: E501
                        }
                    ],
                    "status": "approved",
                    "create_time": "2019-02-26T23:01:16.899Z",
                    "join_url": "https://zoom.us/webinar/mywebinariscool",
                },
            ],
        }

        tbl = Table(
            [
                {
                    "id": "",
                    "email": "barack@obama.com",
                    "first_name": "Barack",
                    "last_name": "Obama",
                    "address": "dsfhkdjsfh st",
                    "city": "jackson heights",
                    "country": "US",
                    "zip": "11371",
                    "state": "NY",
                    "phone": "00000000",
                    "industry": "Food",
                    "org": "Cooking Org",
                    "job_title": "Chef",
                    "purchasing_time_frame": "1-3 months",
                    "role_in_purchase_process": "Influencer",
                    "no_of_employees": "10",
                    "comments": "Looking forward to the Webinar",
                    "custom_questions": [
                        {
                            "title": "What do you hope to learn from this Webinar?",
                            "value": "Look forward to learning how you come up with recipes and services",  # noqa: E501
                        }
                    ],
                    "status": "approved",
                    "create_time": "2019-02-26T23:01:16.899Z",
                    "join_url": "https://zoom.us/webinar/mywebinariscool",
                },
                {
                    "id": "",
                    "email": "joe@biden.com",
                    "first_name": "Joe",
                    "last_name": "Biden",
                    "address": "dsfhkdjsfh st",
                    "city": "jackson heights",
                    "country": "US",
                    "zip": "11371",
                    "state": "NY",
                    "phone": "00000000",
                    "industry": "Food",
                    "org": "Cooking Org",
                    "job_title": "Chef",
                    "purchasing_time_frame": "1-3 months",
                    "role_in_purchase_process": "Influencer",
                    "no_of_employees": "10",
                    "comments": "Looking forward to the Webinar",
                    "custom_questions": [
                        {
                            "title": "What do you hope to learn from this Webinar?",
                            "value": "Look forward to learning how you come up with recipes and services",  # noqa: E501
                        }
                    ],
                    "status": "approved",
                    "create_time": "2019-02-26T23:01:16.899Z",
                    "join_url": "https://zoom.us/webinar/mywebinariscool",
                },
            ]
        )

        m.post(API_AUTH_URL, json={"access_token": "fakeAccessToken"})
        m.get(API_URL + "webinars/123/registrants", json=registrants)
        assert_matching_tables(self.zoom.get_webinar_registrants(123), tbl)

    @requests_mock.Mocker()
    def test_get_meeting_poll_metadata(self, m):
        poll = {
            "id": 1,
            "status": "started",
            "anonymous": "False",
            "poll_type": 1,
            "questions": [
                {
                    "answer_max_character": 1,
                    "answer_min_character": 1,
                    "answer_required": "False",
                    "answers": "Larry David's Curb Your Enthusiasm",
                    "case_sensitive": "True",
                    "name": "Secret Truth",
                    "prompts": [
                        {
                            "prompt_question": "What's the secret truth of the universe?",
                            "prompt_right_answers": [
                                "Pizza delivery",
                                "Larry David's Curb Your Enthusiasm",
                            ],
                        }
                    ],
                    "rating_max_label": "",
                    "rating_max_value": 1,
                    "rating_min_label": "",
                    "rating_min_value": 0,
                    "right_answers": "",
                    "show_as_dropdown": False,
                    "type": "short_answer",
                }
            ],
        }

        tbl = Table(
            [
                {
                    "answer_max_character": 1,
                    "answer_min_character": 1,
                    "answer_required": "False",
                    "answers": "Larry David's Curb Your Enthusiasm",
                    "case_sensitive": "True",
                    "name": "Secret Truth",
                    "rating_max_label": "",
                    "rating_max_value": 1,
                    "rating_min_label": "",
                    "rating_min_value": 0,
                    "right_answers": "",
                    "show_as_dropdown": False,
                    "type": "short_answer",
                    "prompts__prompt_question": "What's the secret truth of the universe?",
                    "prompts__prompt_right_answers": [
                        "Pizza delivery",
                        "Larry David's Curb Your Enthusiasm",
                    ],
                }
            ],
        )

        m.post(API_AUTH_URL, json={"access_token": "fakeAccessToken"})
        m.get(API_URL + "meetings/123/polls/1", json=poll)
        assert_matching_tables(self.zoom.get_meeting_poll_metadata(123, 1), tbl)

    @requests_mock.Mocker()
    def test_get_meeting_all_polls_metadata(self, m):
        polls = {
            "polls": [
                {
                    "id": 1,
                    "status": "started",
                    "anonymous": "False",
                    "poll_type": 1,
                    "questions": [
                        {
                            "answer_max_character": 1,
                            "answer_min_character": 1,
                            "answer_required": "False",
                            "answers": "Larry David's Curb Your Enthusiasm",
                            "case_sensitive": "True",
                            "name": "Secret Truth",
                            "prompts": [
                                {
                                    "prompt_question": "What's the secret truth of the universe?",
                                    "prompt_right_answers": [
                                        "Pizza delivery",
                                        "Larry David's Curb Your Enthusiasm",
                                    ],
                                }
                            ],
                            "rating_max_label": "",
                            "rating_max_value": 1,
                            "rating_min_label": "",
                            "rating_min_value": 0,
                            "right_answers": "",
                            "show_as_dropdown": False,
                            "type": "short_answer",
                        }
                    ],
                },
                {
                    "id": 2,
                    "status": "started",
                    "anonymous": "False",
                    "poll_type": 1,
                    "questions": [
                        {
                            "answer_max_character": 1,
                            "answer_min_character": 1,
                            "answer_required": "False",
                            "answers": "Mets",
                            "case_sensitive": "True",
                            "name": "Play ball",
                            "prompts": [
                                {
                                    "prompt_question": "Best NY baseball team?",
                                    "prompt_right_answers": ["Mets"],
                                }
                            ],
                            "rating_max_label": "",
                            "rating_max_value": 1,
                            "rating_min_label": "",
                            "rating_min_value": 0,
                            "right_answers": "",
                            "show_as_dropdown": True,
                            "type": "short_answer",
                        }
                    ],
                },
            ]
        }

        tbl = Table(
            [
                {
                    "id": 1,
                    "status": "started",
                    "anonymous": "False",
                    "poll_type": 1,
                    "questions__answer_max_character": 1,
                    "questions__answer_min_character": 1,
                    "questions__answer_required": "False",
                    "questions__answers": "Larry David's Curb Your Enthusiasm",
                    "questions__case_sensitive": "True",
                    "questions__name": "Secret Truth",
                    "questions__prompts": [
                        {
                            "prompt_question": "What's the secret truth of the universe?",
                            "prompt_right_answers": [
                                "Pizza delivery",
                                "Larry David's Curb Your Enthusiasm",
                            ],
                        }
                    ],
                    "questions__rating_max_label": "",
                    "questions__rating_max_value": 1,
                    "questions__rating_min_label": "",
                    "questions__rating_min_value": 0,
                    "questions__right_answers": "",
                    "questions__show_as_dropdown": False,
                    "questions__type": "short_answer",
                },
                {
                    "id": 2,
                    "status": "started",
                    "anonymous": "False",
                    "poll_type": 1,
                    "questions__answer_max_character": 1,
                    "questions__answer_min_character": 1,
                    "questions__answer_required": "False",
                    "questions__answers": "Mets",
                    "questions__case_sensitive": "True",
                    "questions__name": "Play ball",
                    "questions__prompts": [
                        {
                            "prompt_question": "Best NY baseball team?",
                            "prompt_right_answers": ["Mets"],
                        }
                    ],
                    "questions__rating_max_label": "",
                    "questions__rating_max_value": 1,
                    "questions__rating_min_label": "",
                    "questions__rating_min_value": 0,
                    "questions__right_answers": "",
                    "questions__show_as_dropdown": True,
                    "questions__type": "short_answer",
                },
            ]
        )

        m.post(API_AUTH_URL, json={"access_token": "fakeAccessToken"})
        m.get(API_URL + "meetings/123/polls", json=polls)
        assert_matching_tables(self.zoom.get_meeting_all_polls_metadata(123), tbl)

    @requests_mock.Mocker()
    def test_get_past_meeting_poll_metadata(self, m):
        poll = {
            "id": 1,
            "status": "started",
            "anonymous": "False",
            "poll_type": 1,
            "questions": [
                {
                    "answer_max_character": 1,
                    "answer_min_character": 1,
                    "answer_required": "False",
                    "answers": "Larry David's Curb Your Enthusiasm",
                    "case_sensitive": "True",
                    "name": "Secret Truth",
                    "prompts": [
                        {
                            "prompt_question": "What's the secret truth of the universe?",
                            "prompt_right_answers": [
                                "Pizza delivery",
                                "Larry David's Curb Your Enthusiasm",
                            ],
                        }
                    ],
                    "rating_max_label": "",
                    "rating_max_value": 1,
                    "rating_min_label": "",
                    "rating_min_value": 0,
                    "right_answers": "",
                    "show_as_dropdown": False,
                    "type": "short_answer",
                }
            ],
        }

        tbl = Table(
            [
                {
                    "answer_max_character": 1,
                    "answer_min_character": 1,
                    "answer_required": "False",
                    "answers": "Larry David's Curb Your Enthusiasm",
                    "case_sensitive": "True",
                    "name": "Secret Truth",
                    "rating_max_label": "",
                    "rating_max_value": 1,
                    "rating_min_label": "",
                    "rating_min_value": 0,
                    "right_answers": "",
                    "show_as_dropdown": False,
                    "type": "short_answer",
                    "prompts__prompt_question": "What's the secret truth of the universe?",
                    "prompts__prompt_right_answers": [
                        "Pizza delivery",
                        "Larry David's Curb Your Enthusiasm",
                    ],
                }
            ]
        )

        m.post(API_AUTH_URL, json={"access_token": "fakeAccessToken"})
        m.get(API_URL + "past_meetings/123/polls", json=poll)
        assert_matching_tables(self.zoom.get_past_meeting_poll_metadata(123), tbl)

    @requests_mock.Mocker()
    def test_get_webinar_poll_metadata(self, m):
        poll = {
            "id": "QalIoKWLTJehBJ8e1xRrbQ",
            "status": "notstart",
            "anonymous": True,
            "poll_type": 2,
            "questions": [
                {
                    "answer_max_character": 200,
                    "answer_min_character": 1,
                    "answer_required": False,
                    "answers": ["Extremely useful"],
                    "case_sensitive": False,
                    "name": "How useful was this meeting?",
                    "prompts": [
                        {
                            "prompt_question": "How are you?",
                            "prompt_right_answers": ["Good"],
                        }
                    ],
                    "rating_max_label": "Extremely Likely",
                    "rating_max_value": 4,
                    "rating_min_label": "Not likely",
                    "rating_min_value": 0,
                    "right_answers": ["Good"],
                    "show_as_dropdown": False,
                    "type": "single",
                }
            ],
            "title": "Learn something new",
        }

        tbl = Table(
            [
                {
                    "answer_max_character": 200,
                    "answer_min_character": 1,
                    "answer_required": False,
                    "answers": ["Extremely useful"],
                    "case_sensitive": False,
                    "name": "How useful was this meeting?",
                    "rating_max_label": "Extremely Likely",
                    "rating_max_value": 4,
                    "rating_min_label": "Not likely",
                    "rating_min_value": 0,
                    "right_answers": ["Good"],
                    "show_as_dropdown": False,
                    "type": "single",
                    "prompts__prompt_question": "How are you?",
                    "prompts__prompt_right_answers": ["Good"],
                }
            ]
        )

        m.post(API_AUTH_URL, json={"access_token": "fakeAccessToken"})
        m.get(API_URL + "webinars/123/polls/456", json=poll)
        assert_matching_tables(self.zoom.get_webinar_poll_metadata(123, 456), tbl)

    @requests_mock.Mocker()
    def test_get_webinar_all_polls_metadata(self, m):
        polls = {
            "polls": [
                {
                    "id": "QalIoKWLTJehBJ8e1xRrbQ",
                    "status": "notstart",
                    "anonymous": True,
                    "poll_type": 2,
                    "questions": [
                        {
                            "answer_max_character": 200,
                            "answer_min_character": 1,
                            "answer_required": False,
                            "answers": ["Extremely useful"],
                            "case_sensitive": False,
                            "name": "How useful was this meeting?",
                            "prompts": [
                                {
                                    "prompt_question": "How are you?",
                                    "prompt_right_answers": ["Good"],
                                }
                            ],
                            "rating_max_label": "Extremely Likely",
                            "rating_max_value": 4,
                            "rating_min_label": "Not likely",
                            "rating_min_value": 0,
                            "right_answers": ["Good"],
                            "show_as_dropdown": False,
                            "type": "single",
                        }
                    ],
                    "title": "Learn something new",
                }
            ],
            "total_records": 1,
        }

        tbl = Table(
            [
                {
                    "id": "QalIoKWLTJehBJ8e1xRrbQ",
                    "status": "notstart",
                    "anonymous": True,
                    "poll_type": 2,
                    "title": "Learn something new",
                    "questions__answer_max_character": 200,
                    "questions__answer_min_character": 1,
                    "questions__answer_required": False,
                    "questions__answers": ["Extremely useful"],
                    "questions__case_sensitive": False,
                    "questions__name": "How useful was this meeting?",
                    "questions__prompts": [
                        {
                            "prompt_question": "How are you?",
                            "prompt_right_answers": ["Good"],
                        }
                    ],
                    "questions__rating_max_label": "Extremely Likely",
                    "questions__rating_max_value": 4,
                    "questions__rating_min_label": "Not likely",
                    "questions__rating_min_value": 0,
                    "questions__right_answers": ["Good"],
                    "questions__show_as_dropdown": False,
                    "questions__type": "single",
                }
            ]
        )

        m.post(API_AUTH_URL, json={"access_token": "fakeAccessToken"})
        m.get(API_URL + "webinars/123/polls", json=polls)
        assert_matching_tables(self.zoom.get_webinar_all_polls_metadata(123), tbl)

    @requests_mock.Mocker()
    def test_get_past_webinar_poll_metadata(self, m):
        poll = {
            "id": "QalIoKWLTJehBJ8e1xRrbQ",
            "status": "notstart",
            "anonymous": True,
            "poll_type": 2,
            "questions": [
                {
                    "answer_max_character": 200,
                    "answer_min_character": 1,
                    "answer_required": False,
                    "answers": ["Extremely useful"],
                    "case_sensitive": False,
                    "name": "How useful was this meeting?",
                    "prompts": [
                        {
                            "prompt_question": "How are you?",
                            "prompt_right_answers": ["Good"],
                        }
                    ],
                    "rating_max_label": "Extremely Likely",
                    "rating_max_value": 4,
                    "rating_min_label": "Not likely",
                    "rating_min_value": 0,
                    "right_answers": ["Good"],
                    "show_as_dropdown": False,
                    "type": "single",
                }
            ],
            "title": "Learn something new",
        }

        tbl = Table(
            [
                {
                    "answer_max_character": 200,
                    "answer_min_character": 1,
                    "answer_required": False,
                    "answers": ["Extremely useful"],
                    "case_sensitive": False,
                    "name": "How useful was this meeting?",
                    "rating_max_label": "Extremely Likely",
                    "rating_max_value": 4,
                    "rating_min_label": "Not likely",
                    "rating_min_value": 0,
                    "right_answers": ["Good"],
                    "show_as_dropdown": False,
                    "type": "single",
                    "prompts__prompt_question": "How are you?",
                    "prompts__prompt_right_answers": ["Good"],
                }
            ],
        )

        m.post(API_AUTH_URL, json={"access_token": "fakeAccessToken"})
        m.get(API_URL + "past_webinars/123/polls", json=poll)
        assert_matching_tables(self.zoom.get_past_webinar_poll_metadata(123), tbl)

    @requests_mock.Mocker()
    def test_get_meeting_poll_results(self, m):
        poll = {
            "id": 123456,
            "uuid": "4444AAAiAAAAAiAiAiiAii==",
            "start_time": "2022-02-01T12:34:12.660Z",
            "questions": [
                {
                    "email": "jchill@example.com",
                    "name": "Jill Chill",
                    "first_name": "Jill",
                    "last_name": "Chill",
                    "question_details": [
                        {
                            "answer": "I am wonderful.",
                            "date_time": "2022-02-01T12:37:12.660Z",
                            "polling_id": "798fGJEWrA",
                            "question": "How are you?",
                        }
                    ],
                }
            ],
        }

        tbl = Table(
            [
                {
                    "email": "jchill@example.com",
                    "name": "Jill Chill",
                    "first_name": "Jill",
                    "last_name": "Chill",
                    "answer": "I am wonderful.",
                    "date_time": "2022-02-01T12:37:12.660Z",
                    "polling_id": "798fGJEWrA",
                    "question": "How are you?",
                }
            ]
        )

        m.post(API_AUTH_URL, json={"access_token": "fakeAccessToken"})
        m.get(API_URL + "report/meetings/123/polls", json=poll)
        assert_matching_tables(self.zoom.get_meeting_poll_results(123), tbl)

    @requests_mock.Mocker()
    def test_get_webinar_poll_results(self, m):
        poll = {
            "id": 123456,
            "questions": [
                {
                    "email": "jchill@example.com",
                    "name": "Jill Chill",
                    "first_name": "Jill",
                    "last_name": "Chill",
                    "question_details": [
                        {
                            "answer": "I am wonderful.",
                            "date_time": "2022-02-01T12:37:12.660Z",
                            "polling_id": "798fGJEWrA",
                            "question": "How are you?",
                        }
                    ],
                }
            ],
            "start_time": "2022-02-01T12:34:12.660Z",
            "uuid": "4444AAAiAAAAAiAiAiiAii==",
        }

        tbl = Table(
            [
                {
                    "email": "jchill@example.com",
                    "name": "Jill Chill",
                    "first_name": "Jill",
                    "last_name": "Chill",
                    "answer": "I am wonderful.",
                    "date_time": "2022-02-01T12:37:12.660Z",
                    "polling_id": "798fGJEWrA",
                    "question": "How are you?",
                }
            ]
        )

        m.post(API_AUTH_URL, json={"access_token": "fakeAccessToken"})
        m.get(API_URL + "report/webinars/123/polls", json=poll)
        assert_matching_tables(self.zoom.get_webinar_poll_results(123), tbl)
