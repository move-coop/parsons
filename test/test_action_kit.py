import json
import os
import unittest
from unittest import mock
from parsons.action_kit.action_kit import ActionKit
from parsons.etl.table import Table

from test.utils import assert_matching_tables

ENV_PARAMETERS = {
    'ACTION_KIT_DOMAIN': 'env_domain',
    'ACTION_KIT_USERNAME': 'env_username',
    'ACTION_KIT_PASSWORD': 'env_password'
}


class TestActionKit(unittest.TestCase):

    def setUp(self):
        self.actionkit = ActionKit(
            domain='domain.actionkit.com',
            username='user',
            password='password'
        )
        self.actionkit.conn = mock.MagicMock()

    def tearDown(self):
        pass

    @mock.patch.dict(os.environ, ENV_PARAMETERS)
    def test_from_envrion(self):
        actionkit = ActionKit()
        self.assertEqual(actionkit.domain, 'env_domain')
        self.assertEqual(actionkit.username, 'env_username')
        self.assertEqual(actionkit.password, 'env_password')

    def test_base_endpoint(self):
        # Test the endpoint
        url = self.actionkit._base_endpoint('user')
        self.assertEqual(url, 'https://domain.actionkit.com/rest/v1/user/')

        url = self.actionkit._base_endpoint('user', 1234)
        self.assertEqual(url, 'https://domain.actionkit.com/rest/v1/user/1234/')

        url = self.actionkit._base_endpoint('user', '1234')
        self.assertEqual(url, 'https://domain.actionkit.com/rest/v1/user/1234/')

    def test_get_user(self):
        # Test get user
        self.actionkit.get_user(123)
        self.actionkit.conn.get.assert_called_with(
            'https://domain.actionkit.com/rest/v1/user/123/',
        )

    def test_get_user_fields(self):
        self.actionkit.get_user_fields()
        self.actionkit.conn.get.assert_called_with(
            'https://domain.actionkit.com/rest/v1/user/schema/'
        )

    def test_create_user(self):
        # Test create user

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.post()).status_code = mock.PropertyMock(return_value=201)
        self.actionkit.conn = resp_mock

        self.actionkit.create_user(email='test')
        self.actionkit.conn.post.assert_called_with(
            'https://domain.actionkit.com/rest/v1/user/',
            data=json.dumps({'email': 'test'})
        )

    def test_update_user(self):
        # Test update user

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.patch()).status_code = mock.PropertyMock(return_value=202)
        self.actionkit.conn = resp_mock

        self.actionkit.update_user(123, last_name='new name')
        self.actionkit.conn.patch.assert_called_with(
            'https://domain.actionkit.com/rest/v1/user/123/',
            data=json.dumps({'last_name': 'new name'})
        )

    def test_delete_user(self):
        # Test delete user

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.patch()).status_code = mock.PropertyMock(return_value=204)
        self.actionkit.conn = resp_mock

        self.actionkit.delete_user(123)
        self.actionkit.conn.delete.assert_called_with(
            'https://domain.actionkit.com/rest/v1/user/123/',
        )

    def test_get_campaign(self):
        # Test get campaign
        self.actionkit.get_campaign(123)
        self.actionkit.conn.get.assert_called_with(
            'https://domain.actionkit.com/rest/v1/campaign/123/',
        )

    def test_create_campaign(self):
        # Test create campaign

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.post()).status_code = mock.PropertyMock(return_value=201)
        self.actionkit.conn = resp_mock

        self.actionkit.create_campaign(name='new_campaign', field='field')
        self.actionkit.conn.post.assert_called_with(
            'https://domain.actionkit.com/rest/v1/campaign/',
            data=json.dumps({
                'name': 'new_campaign',
                'field': 'field'
            })
        )

    def test_get_event_create_page(self):
        # Test get event create page
        self.actionkit.get_event_create_page(123)
        self.actionkit.conn.get.assert_called_with(
            'https://domain.actionkit.com/rest/v1/eventcreatepage/123/',
        )

    def test_create_event_create_page(self):
        # Test create event create page

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.post()).status_code = mock.PropertyMock(return_value=201)
        self.actionkit.conn = resp_mock

        self.actionkit.create_event_create_page(
            name='new_page',
            campaign_id='123',
            title='title'
        )
        self.actionkit.conn.post.assert_called_with(
            'https://domain.actionkit.com/rest/v1/eventcreatepage/',
            data=json.dumps({
                'campaign': '/rest/v1/campaign/123/',
                'name': 'new_page',
                'title': 'title'
            })
        )

    def test_get_event_create_form(self):
        # Test get event create form
        self.actionkit.get_event_create_form(123)
        self.actionkit.conn.get.assert_called_with(
            'https://domain.actionkit.com/rest/v1/eventcreateform/123/',
        )

    def test_create_event_create_form(self):
        # Test event create form

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.post()).status_code = mock.PropertyMock(return_value=201)
        self.actionkit.conn = resp_mock

        self.actionkit.create_event_create_form(
            page_id='123',
            thank_you_text='thank you'
        )
        self.actionkit.conn.post.assert_called_with(
            'https://domain.actionkit.com/rest/v1/eventcreateform/',
            data=json.dumps({
                'page': '/rest/v1/eventcreatepage/123/',
                'thank_you_text': 'thank you'
            })
        )

    def test_get_event_signup_page(self):
        # Test get event signup page
        self.actionkit.get_event_signup_page(123)
        self.actionkit.conn.get.assert_called_with(
            'https://domain.actionkit.com/rest/v1/eventsignuppage/123/',
        )

    def test_create_event_signup_page(self):
        # Test create event signup page

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.post()).status_code = mock.PropertyMock(return_value=201)
        self.actionkit.conn = resp_mock

        self.actionkit.create_event_signup_page(
            name='new_name',
            campaign_id='123',
            title='title'
        )
        self.actionkit.conn.post.assert_called_with(
            'https://domain.actionkit.com/rest/v1/eventsignuppage/',
            data=json.dumps({
                'campaign': '/rest/v1/campaign/123/',
                'name': 'new_name',
                'title': 'title'
            })
        )

    def test_get_event_signup_form(self):
        # Test get event signup form
        self.actionkit.get_event_signup_form(123)
        self.actionkit.conn.get.assert_called_with(
            'https://domain.actionkit.com/rest/v1/eventsignupform/123/',
        )

    def test_create_event_signup_form(self):
        # Test create event signup form

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.post()).status_code = mock.PropertyMock(return_value=201)
        self.actionkit.conn = resp_mock

        self.actionkit.create_event_signup_form(
            page_id='123',
            thank_you_text='thank you'
        )
        self.actionkit.conn.post.assert_called_with(
            'https://domain.actionkit.com/rest/v1/eventsignupform/',
            data=json.dumps({
                'page': '/rest/v1/page/123/',
                'thank_you_text': 'thank you'
            })
        )

    def test_get_page_followup(self):
        # Test get page followup
        self.actionkit.get_page_followup(123)
        self.actionkit.conn.get.assert_called_with(
            'https://domain.actionkit.com/rest/v1/pagefollowup/123/',
        )

    def test_create_page_followup(self):
        # Test create page followup

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.post()).status_code = mock.PropertyMock(return_value=201)
        self.actionkit.conn = resp_mock

        self.actionkit.create_page_followup(
            signup_page_id='123',
            url='url'
        )
        self.actionkit.conn.post.assert_called_with(
            'https://domain.actionkit.com/rest/v1/pagefollowup/',
            data=json.dumps({
                'page': '/rest/v1/eventsignuppage/123/',
                'url': 'url'
            })
        )

    def test_create_generic_action(self):
        # Test create a generic action

        resp_mock = mock.MagicMock()
        type(resp_mock.post()).status_code = mock.PropertyMock(return_value=201)
        self.actionkit.conn = resp_mock

        self.actionkit.create_generic_action(email='bob@bob.com', page='my_action')

        self.actionkit.conn.post.assert_called_with(
            'https://domain.actionkit.com/rest/v1/action/',
            data=json.dumps({'email': 'bob@bob.com', 'page': 'my_action'}))

    def test_bulk_upload_table(self):
        resp_mock = mock.MagicMock()
        type(resp_mock.post()).status_code = mock.PropertyMock(return_value=201)
        self.actionkit._conn = lambda self: resp_mock
        self.actionkit.bulk_upload_table(
            Table([('user_id', 'user_customfield1', 'action_foo'), (5, 'yes', '123 Main St')]),
            'fake_page')
        self.assertEqual(resp_mock.post.call_count, 2)
        name, args, kwargs = resp_mock.method_calls[1]
        self.assertEqual(kwargs['data'],
                         {'page': 'fake_page', 'autocreate_user_fields': 0, 'user_fields_only': 0})
        upload_data = kwargs['files']['upload'].read()
        self.assertEqual(upload_data.decode(),
                         'user_id,user_customfield1,action_foo\r\n5,yes,123 Main St\r\n')

    def test_bulk_upload_table_userfields(self):
        resp_mock = mock.MagicMock()
        type(resp_mock.post()).status_code = mock.PropertyMock(return_value=201)
        self.actionkit._conn = lambda self: resp_mock
        self.actionkit.bulk_upload_table(
            Table([('user_id', 'user_customfield1'), (5, 'yes')]),
            'fake_page')
        self.assertEqual(resp_mock.post.call_count, 2)
        name, args, kwargs = resp_mock.method_calls[1]
        self.assertEqual(kwargs['data'],
                         {'page': 'fake_page', 'autocreate_user_fields': 0, 'user_fields_only': 1})
        self.assertEqual(kwargs['files']['upload'].read().decode(),
                         'user_id,user_customfield1\r\n5,yes\r\n')

    def test_table_split(self):
        test1 = Table([('x', 'y', 'z'), ('a', 'b', ''), ('1', '', '3'), ('4', '', '6')])
        tables = self.actionkit._split_tables_no_empties(test1)
        self.assertEqual(len(tables), 2)
        assert_matching_tables(tables[0], Table([('x', 'y'), ('a', 'b')]))
        assert_matching_tables(tables[1], Table([('x', 'z'), ('1', '3'), ('4', '6')]))

        test2 = Table([('x', 'y', 'z'), ('a', 'b', 'c'), ('1', '2', '3'), ('4', '5', '6')])
        tables2 = self.actionkit._split_tables_no_empties(test2)
        self.assertEqual(len(tables2), 1)
        assert_matching_tables(tables2[0], test2)
