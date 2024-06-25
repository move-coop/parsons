import json
import os
import unittest
from unittest import mock
from parsons import ActionKit, Table

from test.utils import assert_matching_tables

ENV_PARAMETERS = {
    "ACTION_KIT_DOMAIN": "env_domain",
    "ACTION_KIT_USERNAME": "env_username",
    "ACTION_KIT_PASSWORD": "env_password",
}


class TestActionKit(unittest.TestCase):
    def setUp(self):
        self.actionkit = ActionKit(
            domain="domain.actionkit.com", username="user", password="password"
        )
        self.actionkit.conn = mock.MagicMock()

    def tearDown(self):
        pass

    @mock.patch.dict(os.environ, ENV_PARAMETERS)
    def test_from_environ(self):
        actionkit = ActionKit()
        self.assertEqual(actionkit.domain, "env_domain")
        self.assertEqual(actionkit.username, "env_username")
        self.assertEqual(actionkit.password, "env_password")

    def test_base_endpoint(self):
        # Test the endpoint
        url = self.actionkit._base_endpoint("user")
        self.assertEqual(url, "https://domain.actionkit.com/rest/v1/user/")

        url = self.actionkit._base_endpoint("user", 1234)
        self.assertEqual(url, "https://domain.actionkit.com/rest/v1/user/1234/")

        url = self.actionkit._base_endpoint("user", "1234")
        self.assertEqual(url, "https://domain.actionkit.com/rest/v1/user/1234/")

    def test_delete_actionfield(self):
        # Test delete actionfield

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.patch()).status_code = mock.PropertyMock(return_value=204)
        self.actionkit.conn = resp_mock

        self.actionkit.delete_actionfield(123)
        self.actionkit.conn.delete.assert_called_with(
            "https://domain.actionkit.com/rest/v1/actionfield/123/",
        )

    def test_get_user(self):
        # Test get user
        self.actionkit.get_user(123)
        self.actionkit.conn.get.assert_called_with(
            "https://domain.actionkit.com/rest/v1/user/123/", params=None
        )

    def test_get_user_fields(self):
        self.actionkit.get_user_fields()
        self.actionkit.conn.get.assert_called_with(
            "https://domain.actionkit.com/rest/v1/user/schema/", params=None
        )

    def test_create_user(self):
        # Test create user

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.post()).status_code = mock.PropertyMock(return_value=201)
        self.actionkit.conn = resp_mock

        self.actionkit.create_user(email="test")
        self.actionkit.conn.post.assert_called_with(
            "https://domain.actionkit.com/rest/v1/user/",
            data=json.dumps({"email": "test"}),
        )

    def test_add_phone(self):
        # Test add phone

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.post()).status_code = mock.PropertyMock(return_value=201)
        self.actionkit.conn = resp_mock

        self.actionkit.add_phone(user_id=123, phone_type="home", phone="+12025550101")
        self.actionkit.conn.post.assert_called_with(
            "https://domain.actionkit.com/rest/v1/phone/",
            data=json.dumps(
                {
                    "user": "/rest/v1/user/123/",
                    "phone_type": "home",
                    "phone": "+12025550101",
                }
            ),
        )

    def test_update_user(self):
        # Test update user

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.patch()).status_code = mock.PropertyMock(return_value=202)
        self.actionkit.conn = resp_mock

        res = self.actionkit.update_user(123, last_name="new name")
        self.actionkit.conn.patch.assert_called_with(
            "https://domain.actionkit.com/rest/v1/user/123/",
            data=json.dumps({"last_name": "new name"}),
        )

        assert res.status_code == 202

    def test_update_phone(self):
        # Test update phone

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.patch()).status_code = mock.PropertyMock(return_value=202)
        self.actionkit.conn = resp_mock

        res = self.actionkit.update_phone(123, type="mobile")
        self.actionkit.conn.patch.assert_called_with(
            "https://domain.actionkit.com/rest/v1/phone/123/",
            data=json.dumps({"type": "mobile"}),
        )

        assert res.status_code == 202

    def test_update_event(self):
        # Test update event

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.patch()).status_code = mock.PropertyMock(return_value=202)
        self.actionkit.conn = resp_mock
        self.actionkit.update_event(123, is_approved="test")
        self.actionkit.conn.patch.assert_called_with(
            "https://domain.actionkit.com/rest/v1/event/123/",
            data=json.dumps({"is_approved": "test"}),
        )

    def test_create_event_field(self):
        # Test create event field

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.post()).status_code = mock.PropertyMock(return_value=201)
        self.actionkit.conn = resp_mock

        self.actionkit.create_event_field(event_id=123, name="name", value="value")
        self.actionkit.conn.post.assert_called_with(
            "https://domain.actionkit.com/rest/v1/eventfield/",
            data=json.dumps(
                {
                    "event": "/rest/v1/event/123/",
                    "name": "name",
                    "value": "value",
                }
            ),
        )

    def test_update_event_field(self):
        # Test update event field

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.patch()).status_code = mock.PropertyMock(return_value=202)
        self.actionkit.conn = resp_mock
        self.actionkit.update_event_field(456, name="name", value="value")
        self.actionkit.conn.patch.assert_called_with(
            "https://domain.actionkit.com/rest/v1/eventfield/456/",
            data=json.dumps({"name": "name", "value": "value"}),
        )

    def test_get_blackholed_email(self):
        # Test get blackholed email
        resp_mock = mock.MagicMock()
        type(resp_mock.get()).status_code = mock.PropertyMock(return_value=201)
        type(resp_mock.get()).json = lambda x: {"meta": {"next": ""}, "objects": []}
        self.actionkit.conn = resp_mock

        self.actionkit.get_blackholed_email("test")
        self.actionkit.conn.get.assert_called_with(
            "https://domain.actionkit.com/rest/v1/blackholedemail/",
            params={"email": "test", "_limit": 100},
        )

    def test_blackhole_email(self):
        # Test blackhole email

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.post()).status_code = mock.PropertyMock(return_value=201)
        self.actionkit.conn = resp_mock

        self.actionkit.blackhole_email(email="test")
        self.actionkit.conn.post.assert_called_with(
            "https://domain.actionkit.com/rest/v1/blackholedemail/",
            data=json.dumps({"email": "test"}),
        )

    def test_delete_user_data(self):
        # Test delete user data

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.post()).status_code = mock.PropertyMock(return_value=201)
        self.actionkit.conn = resp_mock

        self.actionkit.delete_user_data(email="test")
        self.actionkit.conn.post.assert_called_with(
            "https://domain.actionkit.com/rest/v1/eraser/",
            data=json.dumps({"email": "test"}),
        )

    def test_delete_user(self):
        # Test delete user

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.patch()).status_code = mock.PropertyMock(return_value=204)
        self.actionkit.conn = resp_mock

        self.actionkit.delete_user(123)
        self.actionkit.conn.delete.assert_called_with(
            "https://domain.actionkit.com/rest/v1/user/123/",
        )

    def test_get_campaign(self):
        # Test get campaign
        self.actionkit.get_campaign(123)
        self.actionkit.conn.get.assert_called_with(
            "https://domain.actionkit.com/rest/v1/campaign/123/", params=None
        )

    def test_create_campaign(self):
        # Test create campaign

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.post()).status_code = mock.PropertyMock(return_value=201)
        self.actionkit.conn = resp_mock

        self.actionkit.create_campaign(name="new_campaign", field="field")
        self.actionkit.conn.post.assert_called_with(
            "https://domain.actionkit.com/rest/v1/campaign/",
            data=json.dumps({"name": "new_campaign", "field": "field"}),
        )

    def test_search_events_in_campaign(self):
        # Test search events in campaign
        resp_mock = mock.MagicMock()
        type(resp_mock.get()).status_code = mock.PropertyMock(return_value=201)
        type(resp_mock.get()).json = lambda x: {"meta": {"next": ""}, "objects": []}
        self.actionkit.conn = resp_mock

        self.actionkit.search_events_in_campaign(
            123,
            limit=100,
            order_by="created_at",
            ascdesc="desc",
            filters={
                "title": "Event Title",
                "field__name": "event_field_name",
                "field__value": "Event field value",
            },
            exclude={
                "creator__email": "host@example.com",
            },
        )
        self.actionkit.conn.get.assert_called_with(
            "https://domain.actionkit.com/rest/v1/campaign/123/event_search/",
            params={
                "filter[title]": "Event Title",
                "filter[field__name]": "event_field_name",
                "filter[field__value]": "Event field value",
                "exclude[creator__email]": "host@example.com",
                "order_by": "-created_at",
                "_limit": 100,
            },
        )

    def test_get_event(self):
        # Test get event
        self.actionkit.get_event(1)
        self.actionkit.conn.get.assert_called_with(
            "https://domain.actionkit.com/rest/v1/event/1/", params=None
        )

    def test_get_events(self):
        # Test get events
        resp_mock = mock.MagicMock()
        type(resp_mock.get()).status_code = mock.PropertyMock(return_value=201)
        type(resp_mock.get()).json = lambda x: {"meta": {"next": ""}, "objects": []}
        self.actionkit.conn = resp_mock

        self.actionkit.get_events(100, order_by="created_at")
        self.actionkit.conn.get.assert_called_with(
            "https://domain.actionkit.com/rest/v1/event/",
            params={"order_by": "created_at", "_limit": 100},
        )

    def test_get_event_create_page(self):
        # Test get event create page
        self.actionkit.get_event_create_page(123)
        self.actionkit.conn.get.assert_called_with(
            "https://domain.actionkit.com/rest/v1/eventcreatepage/123/", params=None
        )

    def test_create_event_create_page(self):
        # Test create event create page

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.post()).status_code = mock.PropertyMock(return_value=201)
        self.actionkit.conn = resp_mock

        self.actionkit.create_event_create_page(name="new_page", campaign_id="123", title="title")
        self.actionkit.conn.post.assert_called_with(
            "https://domain.actionkit.com/rest/v1/eventcreatepage/",
            data=json.dumps(
                {
                    "campaign": "/rest/v1/campaign/123/",
                    "name": "new_page",
                    "title": "title",
                }
            ),
        )

    def test_get_event_create_form(self):
        # Test get event create form
        self.actionkit.get_event_create_form(123)
        self.actionkit.conn.get.assert_called_with(
            "https://domain.actionkit.com/rest/v1/eventcreateform/123/", params=None
        )

    def test_create_event_create_form(self):
        # Test event create form

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.post()).status_code = mock.PropertyMock(return_value=201)
        self.actionkit.conn = resp_mock

        self.actionkit.create_event_create_form(page_id="123", thank_you_text="thank you")
        self.actionkit.conn.post.assert_called_with(
            "https://domain.actionkit.com/rest/v1/eventcreateform/",
            data=json.dumps(
                {"page": "/rest/v1/eventcreatepage/123/", "thank_you_text": "thank you"}
            ),
        )

    def test_get_event_signup_page(self):
        # Test get event signup page
        self.actionkit.get_event_signup_page(123)
        self.actionkit.conn.get.assert_called_with(
            "https://domain.actionkit.com/rest/v1/eventsignuppage/123/", params=None
        )

    def test_create_event_signup_page(self):
        # Test create event signup page

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.post()).status_code = mock.PropertyMock(return_value=201)
        self.actionkit.conn = resp_mock

        self.actionkit.create_event_signup_page(name="new_name", campaign_id="123", title="title")
        self.actionkit.conn.post.assert_called_with(
            "https://domain.actionkit.com/rest/v1/eventsignuppage/",
            data=json.dumps(
                {
                    "campaign": "/rest/v1/campaign/123/",
                    "name": "new_name",
                    "title": "title",
                }
            ),
        )

    def test_get_event_signup_form(self):
        # Test get event signup form
        self.actionkit.get_event_signup_form(123)
        self.actionkit.conn.get.assert_called_with(
            "https://domain.actionkit.com/rest/v1/eventsignupform/123/", params=None
        )

    def test_create_event_signup_form(self):
        # Test create event signup form

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.post()).status_code = mock.PropertyMock(return_value=201)
        self.actionkit.conn = resp_mock

        self.actionkit.create_event_signup_form(page_id="123", thank_you_text="thank you")
        self.actionkit.conn.post.assert_called_with(
            "https://domain.actionkit.com/rest/v1/eventsignupform/",
            data=json.dumps({"page": "/rest/v1/page/123/", "thank_you_text": "thank you"}),
        )

    def test_update_event_signup(self):
        # Test update event signup

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.patch()).status_code = mock.PropertyMock(return_value=202)
        self.actionkit.conn = resp_mock
        self.actionkit.update_event_signup(123, email="test")
        self.actionkit.conn.patch.assert_called_with(
            "https://domain.actionkit.com/rest/v1/eventsignup/123/",
            data=json.dumps({"email": "test"}),
        )

    def test_get_mailer(self):
        # Test get mailer
        self.actionkit.get_mailer(123)
        self.actionkit.conn.get.assert_called_with(
            "https://domain.actionkit.com/rest/v1/mailer/123/", params=None
        )

    def test_create_mailer(self):
        # Test create mailer

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.post()).status_code = mock.PropertyMock(return_value=201)
        self.actionkit.conn = resp_mock

        self.actionkit.create_mailer(
            fromline="test <test@test.com>",
            subjects=["test1", "test2"],
            html="<p>test</p>",
        )
        self.actionkit.conn.post.assert_called_with(
            "https://domain.actionkit.com/rest/v1/mailer/",
            data=json.dumps(
                {
                    "fromline": "test <test@test.com>",
                    "subjects": ["test1", "test2"],
                    "html": "<p>test</p>",
                }
            ),
        )

    def test_rebuild_mailer(self):
        # Test rebuild mailer

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.post()).status_code = mock.PropertyMock(return_value=201)
        self.actionkit.conn = resp_mock

        self.actionkit.rebuild_mailer(123)
        self.actionkit.conn.post.assert_called_with(
            "https://domain.actionkit.com/rest/v1/mailer/123/rebuild/",
            data=json.dumps({}),
        )

    def test_queue_mailer(self):
        # Test queue mailer

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.post()).status_code = mock.PropertyMock(return_value=201)
        self.actionkit.conn = resp_mock

        self.actionkit.queue_mailer(123)
        self.actionkit.conn.post.assert_called_with(
            "https://domain.actionkit.com/rest/v1/mailer/123/queue/",
            data=json.dumps({}),
        )

    def test_paginated_get(self):
        # Test paginated_get
        resp_mock = mock.MagicMock()
        first_mock = mock.MagicMock()
        second_mock = mock.MagicMock()
        first_mock.status_code = 201
        first_mock.json = lambda: {
            "meta": {"next": "/rest/v1/user/abc"},
            "objects": list(map(lambda x: {"value": x}, [*range(100)])),
        }
        second_mock.status_code = 201
        second_mock.json = lambda: {
            "meta": {"next": "/rest/v1/user/def"},
            "objects": list(map(lambda x: {"value": x}, [*range(100, 200)])),
        }
        resp_mock.get.side_effect = [first_mock, second_mock]
        self.actionkit.conn = resp_mock
        results = self.actionkit.paginated_get("user", 150, order_by="created_at")
        self.assertEqual(results.num_rows, 150)
        calls = [
            unittest.mock.call(
                "https://domain.actionkit.com/rest/v1/user/",
                params={"order_by": "created_at", "_limit": 100},
            ),
            unittest.mock.call("https://domain.actionkit.com/rest/v1/user/abc"),
        ]
        self.actionkit.conn.get.assert_has_calls(calls)

    def test_paginated_get_custom_limit(self):
        # Test paginated_get
        resp_mock = mock.MagicMock()
        first_mock = mock.MagicMock()
        second_mock = mock.MagicMock()
        first_mock.status_code = 201
        first_mock.json = lambda: {
            "meta": {"next": "/rest/v1/user/abc"},
            "objects": list(map(lambda x: {"value": x}, [*range(100)])),
        }
        second_mock.status_code = 201
        second_mock.json = lambda: {
            "meta": {"next": "/rest/v1/user/def"},
            "objects": list(map(lambda x: {"value": x}, [*range(100, 200)])),
        }
        resp_mock.get.side_effect = [first_mock, second_mock]
        self.actionkit.conn = resp_mock
        results = self.actionkit.paginated_get_custom_limit("user", 150, "value", 102)
        self.assertEqual(results.num_rows, 102)
        self.assertEqual(results.column_data("value")[0], 0)
        self.assertEqual(results.column_data("value")[-1], 101)
        calls = [
            unittest.mock.call(
                "https://domain.actionkit.com/rest/v1/user/",
                params={"order_by": "value", "_limit": 100},
            ),
            unittest.mock.call("https://domain.actionkit.com/rest/v1/user/abc"),
        ]
        self.actionkit.conn.get.assert_has_calls(calls)

    def test_get_order(self):
        # Test get order
        self.actionkit.get_order(123)
        self.actionkit.conn.get.assert_called_with(
            "https://domain.actionkit.com/rest/v1/order/123/", params=None
        )

    def test_update_order(self):
        # Test update order

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.patch()).status_code = mock.PropertyMock(return_value=202)
        self.actionkit.conn = resp_mock
        self.actionkit.update_order(123, account="test")
        self.actionkit.conn.patch.assert_called_with(
            "https://domain.actionkit.com/rest/v1/order/123/",
            data=json.dumps({"account": "test"}),
        )

    def test_update_order_user_detail(self):
        # Test update order user detail

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.patch()).status_code = mock.PropertyMock(return_value=202)
        self.actionkit.conn = resp_mock

        res = self.actionkit.update_order_user_detail(123, first_name="new name")
        self.actionkit.conn.patch.assert_called_with(
            "https://domain.actionkit.com/rest/v1/orderuserdetail/123/",
            data=json.dumps({"first_name": "new name"}),
        )

        assert res.status_code == 202

    def test_get_orders(self):
        # Test get orders
        resp_mock = mock.MagicMock()
        type(resp_mock.get()).status_code = mock.PropertyMock(return_value=201)
        type(resp_mock.get()).json = lambda x: {"meta": {"next": ""}, "objects": []}
        self.actionkit.conn = resp_mock

        self.actionkit.get_orders(100, order_by="created_at")
        self.actionkit.conn.get.assert_called_with(
            "https://domain.actionkit.com/rest/v1/order/",
            params={"order_by": "created_at", "_limit": 100},
        )

    def test_update_paymenttoken(self):
        # Test update payment token

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.patch()).status_code = mock.PropertyMock(return_value=202)
        self.actionkit.conn = resp_mock

        self.actionkit.update_paymenttoken(1, status="inactive")
        self.actionkit.conn.patch.assert_called_with(
            "https://domain.actionkit.com/rest/v1/paymenttoken/1/",
            data=json.dumps({"status": "inactive"}),
        )

    def test_get_page_followup(self):
        # Test get page followup
        self.actionkit.get_page_followup(123)
        self.actionkit.conn.get.assert_called_with(
            "https://domain.actionkit.com/rest/v1/pagefollowup/123/", params=None
        )

    def test_create_page_followup(self):
        # Test create page followup

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.post()).status_code = mock.PropertyMock(return_value=201)
        self.actionkit.conn = resp_mock

        self.actionkit.create_page_followup(signup_page_id="123", url="url")
        self.actionkit.conn.post.assert_called_with(
            "https://domain.actionkit.com/rest/v1/pagefollowup/",
            data=json.dumps({"page": "/rest/v1/eventsignuppage/123/", "url": "url"}),
        )

    def test_get_survey_question(self):
        # Test get survey question
        self.actionkit.get_survey_question(123)
        self.actionkit.conn.get.assert_called_with(
            "https://domain.actionkit.com/rest/v1/surveyquestion/123/", params=None
        )

    def test_update_survey_question(self):
        # Test update survey question

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.patch()).status_code = mock.PropertyMock(return_value=202)
        self.actionkit.conn = resp_mock
        self.actionkit.update_survey_question(123, question_html="test")
        self.actionkit.conn.patch.assert_called_with(
            "https://domain.actionkit.com/rest/v1/surveyquestion/123/",
            data=json.dumps({"question_html": "test"}),
        )

    def test_get_orderrecurring(self):
        # Test get orderrecurring
        self.actionkit.get_orderrecurring(123)
        self.actionkit.conn.get.assert_called_with(
            "https://domain.actionkit.com/rest/v1/orderrecurring/123/", params=None
        )

    def test_cancel_orderrecurring(self):
        # Test cancel recurring order

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.post()).status_code = mock.PropertyMock(return_value=201)
        self.actionkit.conn = resp_mock

        self.actionkit.cancel_orderrecurring(1)
        self.actionkit.conn.post.assert_called_with(
            "https://domain.actionkit.com/rest/v1/orderrecurring/1/cancel/"
        )

    def test_update_orderrecurring(self):
        # Test update orderrecurring

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.patch()).status_code = mock.PropertyMock(return_value=202)
        self.actionkit.conn = resp_mock
        self.actionkit.update_orderrecurring(123, amount="1.00")
        self.actionkit.conn.patch.assert_called_with(
            "https://domain.actionkit.com/rest/v1/orderrecurring/123/",
            data=json.dumps({"amount": "1.00"}),
        )

    def test_create_transaction(self):
        # Test create transaction

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.post()).status_code = mock.PropertyMock(return_value=201)
        self.actionkit.conn = resp_mock

        self.actionkit.create_transaction(
            account="Account",
            amount=1,
            amount_converted=1,
            currency="USD",
            failure_code="",
            failure_description="",
            failure_message="",
            order="/rest/v1/order/1/",
            status="completed",
            success=True,
            test_mode=False,
            trans_id="abc123",
            type="sale",
        )
        self.actionkit.conn.post.assert_called_with(
            "https://domain.actionkit.com/rest/v1/transaction/",
            data=json.dumps(
                {
                    "account": "Account",
                    "amount": 1,
                    "amount_converted": 1,
                    "currency": "USD",
                    "failure_code": "",
                    "failure_description": "",
                    "failure_message": "",
                    "order": "/rest/v1/order/1/",
                    "status": "completed",
                    "success": True,
                    "test_mode": False,
                    "trans_id": "abc123",
                    "type": "sale",
                }
            ),
        )

    def test_update_transaction(self):
        # Test update transaction

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.patch()).status_code = mock.PropertyMock(return_value=202)
        self.actionkit.conn = resp_mock
        self.actionkit.update_transaction(123, account="test")
        self.actionkit.conn.patch.assert_called_with(
            "https://domain.actionkit.com/rest/v1/transaction/123/",
            data=json.dumps({"account": "test"}),
        )

    def test_get_transactions(self):
        # Test get transactions
        resp_mock = mock.MagicMock()
        type(resp_mock.get()).status_code = mock.PropertyMock(return_value=201)
        type(resp_mock.get()).json = lambda x: {"meta": {"next": ""}, "objects": []}
        self.actionkit.conn = resp_mock

        self.actionkit.get_transactions(100, order_by="created_at")
        self.actionkit.conn.get.assert_called_with(
            "https://domain.actionkit.com/rest/v1/transaction/",
            params={"order_by": "created_at", "_limit": 100},
        )

    def test_create_generic_action(self):
        # Test create a generic action

        resp_mock = mock.MagicMock()
        type(resp_mock.post()).status_code = mock.PropertyMock(return_value=201)
        self.actionkit.conn = resp_mock

        self.actionkit.create_generic_action(email="bob@bob.com", page="my_action")

        self.actionkit.conn.post.assert_called_with(
            "https://domain.actionkit.com/rest/v1/action/",
            data=json.dumps({"email": "bob@bob.com", "page": "my_action"}),
        )

    def test_update_import_action(self):
        # Test update import action

        # Mock resp and status code
        resp_mock = mock.MagicMock()
        type(resp_mock.patch()).status_code = mock.PropertyMock(return_value=202)
        self.actionkit.conn = resp_mock

        res = self.actionkit.update_import_action(123, source="new source")
        self.actionkit.conn.patch.assert_called_with(
            "https://domain.actionkit.com/rest/v1/importaction/123/",
            data=json.dumps({"source": "new source"}),
        )

        assert res.status_code == 202

    def test_bulk_upload_table(self):
        resp_mock = mock.MagicMock()
        type(resp_mock.post()).status_code = mock.PropertyMock(return_value=201)
        self.actionkit._conn = lambda self: resp_mock
        self.actionkit.bulk_upload_table(
            Table(
                [
                    ("user_id", "user_customfield1", "action_foo"),
                    (5, "yes", "123 Main St"),
                ]
            ),
            "fake_page",
        )
        self.assertEqual(resp_mock.post.call_count, 2)
        name, args, kwargs = resp_mock.method_calls[1]
        self.assertEqual(
            kwargs["data"],
            {"page": "fake_page", "autocreate_user_fields": 0, "user_fields_only": 0},
        )
        upload_data = kwargs["files"]["upload"].read()
        self.assertEqual(
            upload_data.decode(),
            "user_id,user_customfield1,action_foo\r\n5,yes,123 Main St\r\n",
        )

    def test_bulk_upload_table_userfields(self):
        resp_mock = mock.MagicMock()
        type(resp_mock.post()).status_code = mock.PropertyMock(return_value=201)
        self.actionkit._conn = lambda self: resp_mock
        self.actionkit.bulk_upload_table(
            Table([("user_id", "user_customfield1"), (5, "yes")]), "fake_page"
        )
        self.assertEqual(resp_mock.post.call_count, 2)
        name, args, kwargs = resp_mock.method_calls[1]
        self.assertEqual(
            kwargs["data"],
            {"page": "fake_page", "autocreate_user_fields": 0, "user_fields_only": 1},
        )
        self.assertEqual(
            kwargs["files"]["upload"].read().decode(),
            "user_id,user_customfield1\r\n5,yes\r\n",
        )

    def test_table_split(self):
        test1 = Table([("x", "y", "z"), ("a", "b", ""), ("1", "", "3"), ("4", "", "6")])
        tables = self.actionkit._split_tables_no_empties(test1, True, [])
        self.assertEqual(len(tables), 2)
        assert_matching_tables(tables[0], Table([("x", "y"), ("a", "b")]))
        assert_matching_tables(tables[1], Table([("x", "z"), ("1", "3"), ("4", "6")]))

        test2 = Table([("x", "y", "z"), ("a", "b", "c"), ("1", "2", "3"), ("4", "5", "6")])
        tables2 = self.actionkit._split_tables_no_empties(test2, True, [])
        self.assertEqual(len(tables2), 1)
        assert_matching_tables(tables2[0], test2)

        test3 = Table([("x", "y", "z"), ("a", "b", ""), ("1", "2", "3"), ("4", "5", "6")])
        tables3 = self.actionkit._split_tables_no_empties(test3, False, ["z"])
        self.assertEqual(len(tables3), 2)
        assert_matching_tables(tables3[0], Table([("x", "y"), ("a", "b")]))
        assert_matching_tables(
            tables3[1], Table([("x", "y", "z"), ("1", "2", "3"), ("4", "5", "6")])
        )

    def test_collect_errors(self):
        resp_mock = mock.MagicMock()
        type(resp_mock.get()).json = lambda x: {"is_completed": True, "has_errors": 25}
        self.actionkit.conn = resp_mock

        self.actionkit.collect_upload_errors([{"id": "12345"}])

        self.actionkit.conn.get.assert_any_call(
            "https://domain.actionkit.com/rest/v1/upload/12345/", params=None
        )

        # With 25 errors, we will view two pages
        self.actionkit.conn.get.assert_any_call(
            "https://domain.actionkit.com/rest/v1/uploaderror/",
            params={"upload": "12345", "_limit": 20, "_offset": 0},
        )
        self.actionkit.conn.get.assert_any_call(
            "https://domain.actionkit.com/rest/v1/uploaderror/",
            params={"upload": "12345", "_limit": 20, "_offset": 20},
        )

        # Assert that we don't attempt to view a third page
        assert (
            mock.call(
                "https://domain.actionkit.com/rest/v1/uploaderror/",
                params={"upload": "12345", "_limit": 20, "_offset": 40},
            )
            not in self.actionkit.conn.get.call_args_list
        ), "Called with invalid arguments."
