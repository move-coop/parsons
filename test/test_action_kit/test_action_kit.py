"""Tests for the ActionKit connector.

ActionKit talks to its REST API through a ``requests.Session`` (``self.conn``), so
the correct boundary to mock is the HTTP layer: the ``requests_mock`` fixture
intercepts the real Session and lets the connector's own URL building, request
bodies, response parsing (``_base_get``/``_base_post``), and pagination run for real.
The previous suite replaced ``self.conn`` with a ``MagicMock``, which never
exercised any of that — it only checked that a method was handed the right URL.
"""

import re
from urllib.parse import parse_qs, urlsplit

from requests_toolbelt.multipart.decoder import MultipartDecoder

from parsons import ActionKit, Table
from test.conftest import assert_matching_tables

BASE = "https://domain.actionkit.com/rest/v1"
# _base_post returns the created object's Location header, so every POST mock supplies one.
LOCATION = f"{BASE}/thing/1/"

ENV_PARAMETERS = {
    "ACTION_KIT_DOMAIN": "env_domain",
    "ACTION_KIT_USERNAME": "env_username",
    "ACTION_KIT_PASSWORD": "env_password",
}


def query(request):
    """The request's query string parsed to ``{name: [values]}`` (case preserved)."""
    return parse_qs(urlsplit(request.url).query)


def multipart_fields(request):
    """Parse a multipart request body into ``{field_name: raw_bytes}``."""
    fields = {}
    for part in MultipartDecoder(request.body, request.headers["Content-Type"]).parts:
        disposition = part.headers[b"Content-Disposition"].decode()
        name = re.search(r'name="([^"]+)"', disposition).group(1)
        fields[name] = part.content
    return fields


def test_from_environ(monkeypatch):
    for key, value in ENV_PARAMETERS.items():
        monkeypatch.setenv(key, value)

    actionkit = ActionKit()

    assert actionkit.domain == "env_domain"
    assert actionkit.username == "env_username"
    assert actionkit.password == "env_password"


def test_base_endpoint(ak):
    assert ak._base_endpoint("user") == f"{BASE}/user/"
    assert ak._base_endpoint("user", 1234) == f"{BASE}/user/1234/"
    assert ak._base_endpoint("user", "1234") == f"{BASE}/user/1234/"


def test_delete_actionfield(ak, requests_mock):
    requests_mock.delete(f"{BASE}/actionfield/123/", status_code=204)

    ak.delete_actionfield(123)

    assert requests_mock.last_request.method == "DELETE"
    assert requests_mock.last_request.url == f"{BASE}/actionfield/123/"


def test_get_user(ak, requests_mock):
    requests_mock.get(f"{BASE}/user/123/", json={"id": 123})

    assert ak.get_user(123) == {"id": 123}
    assert query(requests_mock.last_request) == {}


def test_get_user_fields(ak, requests_mock):
    # get_user_fields returns the field names, i.e. list(resp["fields"].keys()).
    requests_mock.get(f"{BASE}/user/schema/", json={"fields": {"first_name": {}, "last_name": {}}})

    assert ak.get_user_fields() == ["first_name", "last_name"]
    assert query(requests_mock.last_request) == {}


def test_create_user(ak, requests_mock):
    requests_mock.post(f"{BASE}/user/", status_code=201, json={}, headers={"Location": LOCATION})

    assert ak.create_user(email="test") == LOCATION
    assert requests_mock.last_request.json() == {"email": "test"}


def test_add_phone(ak, requests_mock):
    requests_mock.post(f"{BASE}/phone/", status_code=201, json={}, headers={"Location": LOCATION})

    ak.add_phone(user_id=123, phone_type="home", phone="+12025550101")

    assert requests_mock.last_request.json() == {
        "user": "/rest/v1/user/123/",
        "phone_type": "home",
        "phone": "+12025550101",
    }


def test_update_user(ak, requests_mock):
    requests_mock.patch(f"{BASE}/user/123/", status_code=202)

    resp = ak.update_user(123, last_name="new name")

    assert requests_mock.last_request.json() == {"last_name": "new name"}
    assert resp.status_code == 202


def test_update_phone(ak, requests_mock):
    requests_mock.patch(f"{BASE}/phone/123/", status_code=202)

    res = ak.update_phone(123, type="mobile")

    assert requests_mock.last_request.json() == {"type": "mobile"}
    assert res.status_code == 202


def test_update_event(ak, requests_mock):
    requests_mock.patch(f"{BASE}/event/123/", status_code=202)

    ak.update_event(123, is_approved="test")

    assert requests_mock.last_request.json() == {"is_approved": "test"}


def test_create_event_field(ak, requests_mock):
    requests_mock.post(
        f"{BASE}/eventfield/", status_code=201, json={}, headers={"Location": LOCATION}
    )

    ak.create_event_field(event_id=123, name="name", value="value")

    assert requests_mock.last_request.json() == {
        "event": "/rest/v1/event/123/",
        "name": "name",
        "value": "value",
    }


def test_update_event_field(ak, requests_mock):
    requests_mock.patch(f"{BASE}/eventfield/456/", status_code=202)

    ak.update_event_field(456, name="name", value="value")

    assert requests_mock.last_request.json() == {"name": "name", "value": "value"}


def test_get_blackholed_email(ak, requests_mock):
    requests_mock.get(f"{BASE}/blackholedemail/", json={"meta": {"next": ""}, "objects": []})

    tbl = ak.get_blackholed_email("test")

    assert tbl.num_rows == 0
    assert query(requests_mock.last_request) == {"email": ["test"], "_limit": ["100"]}


def test_blackhole_email(ak, requests_mock):
    requests_mock.post(
        f"{BASE}/blackholedemail/", status_code=201, json={}, headers={"Location": LOCATION}
    )

    ak.blackhole_email(email="test")

    assert requests_mock.last_request.json() == {"email": "test"}


def test_delete_user_data(ak, requests_mock):
    requests_mock.post(f"{BASE}/eraser/", status_code=201, json={}, headers={"Location": LOCATION})

    ak.delete_user_data(email="test")

    assert requests_mock.last_request.json() == {"email": "test"}


def test_delete_user(ak, requests_mock):
    requests_mock.delete(f"{BASE}/user/123/", status_code=204)

    ak.delete_user(123)

    assert requests_mock.last_request.method == "DELETE"
    assert requests_mock.last_request.url == f"{BASE}/user/123/"


def test_get_campaign(ak, requests_mock):
    requests_mock.get(f"{BASE}/campaign/123/", json={"id": 123})

    assert ak.get_campaign(123) == {"id": 123}
    assert query(requests_mock.last_request) == {}


def test_create_campaign(ak, requests_mock):
    requests_mock.post(
        f"{BASE}/campaign/", status_code=201, json={}, headers={"Location": LOCATION}
    )

    ak.create_campaign(name="new_campaign", field="field")

    assert requests_mock.last_request.json() == {"name": "new_campaign", "field": "field"}


def test_search_events_in_campaign(ak, requests_mock):
    requests_mock.get(
        f"{BASE}/campaign/123/event_search/", json={"meta": {"next": ""}, "objects": []}
    )

    ak.search_events_in_campaign(
        123,
        limit=100,
        order_by="created_at",
        ascdesc="desc",
        filters={
            "title": "Event Title",
            "field__name": "event_field_name",
            "field__value": "Event field value",
        },
        exclude={"creator__email": "host@example.com"},
    )

    assert query(requests_mock.last_request) == {
        "filter[title]": ["Event Title"],
        "filter[field__name]": ["event_field_name"],
        "filter[field__value]": ["Event field value"],
        "exclude[creator__email]": ["host@example.com"],
        "order_by": ["-created_at"],
        "_limit": ["100"],
    }


def test_get_event(ak, requests_mock):
    requests_mock.get(f"{BASE}/event/1/", json={"id": 1})

    assert ak.get_event(1) == {"id": 1}
    assert query(requests_mock.last_request) == {}


def test_get_events(ak, requests_mock):
    requests_mock.get(f"{BASE}/event/", json={"meta": {"next": ""}, "objects": []})

    tbl = ak.get_events(100, order_by="created_at")

    assert tbl.num_rows == 0
    assert query(requests_mock.last_request) == {"order_by": ["created_at"], "_limit": ["100"]}


def test_get_event_create_page(ak, requests_mock):
    requests_mock.get(f"{BASE}/eventcreatepage/123/", json={"id": 123})

    assert ak.get_event_create_page(123) == {"id": 123}
    assert query(requests_mock.last_request) == {}


def test_create_event_create_page(ak, requests_mock):
    requests_mock.post(
        f"{BASE}/eventcreatepage/", status_code=201, json={}, headers={"Location": LOCATION}
    )

    ak.create_event_create_page(name="new_page", campaign_id="123", title="title")

    assert requests_mock.last_request.json() == {
        "campaign": "/rest/v1/campaign/123/",
        "name": "new_page",
        "title": "title",
    }


def test_get_event_create_form(ak, requests_mock):
    requests_mock.get(f"{BASE}/eventcreateform/123/", json={"id": 123})

    assert ak.get_event_create_form(123) == {"id": 123}
    assert query(requests_mock.last_request) == {}


def test_create_event_create_form(ak, requests_mock):
    requests_mock.post(
        f"{BASE}/eventcreateform/", status_code=201, json={}, headers={"Location": LOCATION}
    )

    ak.create_event_create_form(page_id="123", thank_you_text="thank you")

    assert requests_mock.last_request.json() == {
        "page": "/rest/v1/eventcreatepage/123/",
        "thank_you_text": "thank you",
    }


def test_get_event_signup_page(ak, requests_mock):
    requests_mock.get(f"{BASE}/eventsignuppage/123/", json={"id": 123})

    assert ak.get_event_signup_page(123) == {"id": 123}
    assert query(requests_mock.last_request) == {}


def test_create_event_signup_page(ak, requests_mock):
    requests_mock.post(
        f"{BASE}/eventsignuppage/", status_code=201, json={}, headers={"Location": LOCATION}
    )

    ak.create_event_signup_page(name="new_name", campaign_id="123", title="title")

    assert requests_mock.last_request.json() == {
        "campaign": "/rest/v1/campaign/123/",
        "name": "new_name",
        "title": "title",
    }


def test_get_event_signup_form(ak, requests_mock):
    requests_mock.get(f"{BASE}/eventsignupform/123/", json={"id": 123})

    assert ak.get_event_signup_form(123) == {"id": 123}
    assert query(requests_mock.last_request) == {}


def test_create_event_signup_form(ak, requests_mock):
    requests_mock.post(
        f"{BASE}/eventsignupform/", status_code=201, json={}, headers={"Location": LOCATION}
    )

    ak.create_event_signup_form(page_id="123", thank_you_text="thank you")

    assert requests_mock.last_request.json() == {
        "page": "/rest/v1/page/123/",
        "thank_you_text": "thank you",
    }


def test_update_event_signup(ak, requests_mock):
    requests_mock.patch(f"{BASE}/eventsignup/123/", status_code=202)

    ak.update_event_signup(123, email="test")

    assert requests_mock.last_request.json() == {"email": "test"}


def test_get_mailer(ak, requests_mock):
    requests_mock.get(f"{BASE}/mailer/123/", json={"id": 123})

    assert ak.get_mailer(123) == {"id": 123}
    assert query(requests_mock.last_request) == {}


def test_create_mailer(ak, requests_mock):
    requests_mock.post(f"{BASE}/mailer/", status_code=201, json={}, headers={"Location": LOCATION})

    ak.create_mailer(
        fromline="test <test@test.com>", subjects=["test1", "test2"], html="<p>test</p>"
    )

    assert requests_mock.last_request.json() == {
        "fromline": "test <test@test.com>",
        "subjects": ["test1", "test2"],
        "html": "<p>test</p>",
    }


def test_rebuild_mailer(ak, requests_mock):
    requests_mock.post(
        f"{BASE}/mailer/123/rebuild/", status_code=201, json={}, headers={"Location": LOCATION}
    )

    ak.rebuild_mailer(123)

    assert requests_mock.last_request.json() == {}


def test_queue_mailer(ak, requests_mock):
    requests_mock.post(
        f"{BASE}/mailer/123/queue/", status_code=201, json={}, headers={"Location": LOCATION}
    )

    ak.queue_mailer(123)

    assert requests_mock.last_request.json() == {}


def test_paginated_get(ak, requests_mock):
    requests_mock.get(
        f"{BASE}/user/",
        json={"meta": {"next": "/rest/v1/user/abc"}, "objects": [{"value": x} for x in range(100)]},
    )
    requests_mock.get(
        f"{BASE}/user/abc",
        json={
            "meta": {"next": "/rest/v1/user/def"},
            "objects": [{"value": x} for x in range(100, 200)],
        },
    )

    results = ak.paginated_get("user", 150, order_by="created_at")

    assert results.num_rows == 150
    history = requests_mock.request_history
    assert query(history[0]) == {"order_by": ["created_at"], "_limit": ["100"]}
    assert history[1].url == f"{BASE}/user/abc"


def test_paginated_get_custom_limit(ak, requests_mock):
    requests_mock.get(
        f"{BASE}/user/",
        json={"meta": {"next": "/rest/v1/user/abc"}, "objects": [{"value": x} for x in range(100)]},
    )
    requests_mock.get(
        f"{BASE}/user/abc",
        json={
            "meta": {"next": "/rest/v1/user/def"},
            "objects": [{"value": x} for x in range(100, 200)],
        },
    )

    results = ak.paginated_get_custom_limit("user", 150, "value", 102)

    assert results.num_rows == 102
    assert results.column_data("value")[0] == 0
    assert results.column_data("value")[-1] == 101
    history = requests_mock.request_history
    assert query(history[0]) == {"order_by": ["value"], "_limit": ["100"]}
    assert history[1].url == f"{BASE}/user/abc"


def test_get_order(ak, requests_mock):
    requests_mock.get(f"{BASE}/order/123/", json={"id": 123})

    assert ak.get_order(123) == {"id": 123}
    assert query(requests_mock.last_request) == {}


def test_update_order(ak, requests_mock):
    requests_mock.patch(f"{BASE}/order/123/", status_code=202)

    ak.update_order(123, account="test")

    assert requests_mock.last_request.json() == {"account": "test"}


def test_update_order_user_detail(ak, requests_mock):
    requests_mock.patch(f"{BASE}/orderuserdetail/123/", status_code=202)

    res = ak.update_order_user_detail(123, first_name="new name")

    assert requests_mock.last_request.json() == {"first_name": "new name"}
    assert res.status_code == 202


def test_get_orders(ak, requests_mock):
    requests_mock.get(f"{BASE}/order/", json={"meta": {"next": ""}, "objects": []})

    tbl = ak.get_orders(100, order_by="created_at")

    assert tbl.num_rows == 0
    assert query(requests_mock.last_request) == {"order_by": ["created_at"], "_limit": ["100"]}


def test_update_paymenttoken(ak, requests_mock):
    requests_mock.patch(f"{BASE}/paymenttoken/1/", status_code=202)

    ak.update_paymenttoken(1, status="inactive")

    assert requests_mock.last_request.json() == {"status": "inactive"}


def test_get_page_followup(ak, requests_mock):
    requests_mock.get(f"{BASE}/pagefollowup/123/", json={"id": 123})

    assert ak.get_page_followup(123) == {"id": 123}
    assert query(requests_mock.last_request) == {}


def test_create_page_followup(ak, requests_mock):
    requests_mock.post(
        f"{BASE}/pagefollowup/", status_code=201, json={}, headers={"Location": LOCATION}
    )

    ak.create_page_followup(signup_page_id="123", url="url")

    assert requests_mock.last_request.json() == {
        "page": "/rest/v1/eventsignuppage/123/",
        "url": "url",
    }


def test_get_survey_question(ak, requests_mock):
    requests_mock.get(f"{BASE}/surveyquestion/123/", json={"id": 123})

    assert ak.get_survey_question(123) == {"id": 123}
    assert query(requests_mock.last_request) == {}


def test_update_survey_question(ak, requests_mock):
    requests_mock.patch(f"{BASE}/surveyquestion/123/", status_code=202)

    ak.update_survey_question(123, question_html="test")

    assert requests_mock.last_request.json() == {"question_html": "test"}


def test_get_orderrecurring(ak, requests_mock):
    requests_mock.get(f"{BASE}/orderrecurring/123/", json={"id": 123})

    assert ak.get_orderrecurring(123) == {"id": 123}
    assert query(requests_mock.last_request) == {}


def test_cancel_orderrecurring(ak, requests_mock):
    requests_mock.post(
        f"{BASE}/orderrecurring/1/cancel/", status_code=201, json={}, headers={"Location": LOCATION}
    )

    ak.cancel_orderrecurring(1)

    assert requests_mock.last_request.method == "POST"
    assert requests_mock.last_request.url == f"{BASE}/orderrecurring/1/cancel/"


def test_update_orderrecurring(ak, requests_mock):
    requests_mock.patch(f"{BASE}/orderrecurring/123/", status_code=202)

    ak.update_orderrecurring(123, amount="1.00")

    assert requests_mock.last_request.json() == {"amount": "1.00"}


def test_create_transaction(ak, requests_mock):
    requests_mock.post(
        f"{BASE}/transaction/", status_code=201, json={}, headers={"Location": LOCATION}
    )

    ak.create_transaction(
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

    assert requests_mock.last_request.json() == {
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


def test_update_transaction(ak, requests_mock):
    requests_mock.patch(f"{BASE}/transaction/123/", status_code=202)

    ak.update_transaction(123, account="test")

    assert requests_mock.last_request.json() == {"account": "test"}


def test_get_transactions(ak, requests_mock):
    requests_mock.get(f"{BASE}/transaction/", json={"meta": {"next": ""}, "objects": []})

    tbl = ak.get_transactions(100, order_by="created_at")

    assert tbl.num_rows == 0
    assert query(requests_mock.last_request) == {"order_by": ["created_at"], "_limit": ["100"]}


def test_create_generic_action(ak, requests_mock):
    requests_mock.post(f"{BASE}/action/", status_code=201, json={}, headers={"Location": LOCATION})

    ak.create_generic_action(email="bob@bob.com", page="my_action")

    assert requests_mock.last_request.json() == {"email": "bob@bob.com", "page": "my_action"}


def test_update_import_action(ak, requests_mock):
    requests_mock.patch(f"{BASE}/importaction/123/", status_code=202)

    res = ak.update_import_action(123, source="new source")

    assert requests_mock.last_request.json() == {"source": "new source"}
    assert res.status_code == 202


def test_bulk_upload_table(ak, requests_mock):
    requests_mock.post(
        f"{BASE}/upload/", status_code=201, headers={"Location": f"{BASE}/upload/98765/"}
    )

    result = ak.bulk_upload_table(
        Table([("user_id", "user_customfield1", "action_foo"), (5, "yes", "123 Main St")]),
        "fake_page",
    )

    assert result["success"] is True
    assert result["results"][0]["id"] == "98765"
    fields = multipart_fields(requests_mock.last_request)
    assert fields["page"] == b"fake_page"
    assert fields["autocreate_user_fields"] == b"0"
    assert fields["user_fields_only"] == b"0"
    assert (
        fields["upload"].decode() == "user_id,user_customfield1,action_foo\r\n5,yes,123 Main St\r\n"
    )


def test_bulk_upload_table_userfields(ak, requests_mock):
    requests_mock.post(
        f"{BASE}/upload/", status_code=201, headers={"Location": f"{BASE}/upload/98765/"}
    )

    ak.bulk_upload_table(Table([("user_id", "user_customfield1"), (5, "yes")]), "fake_page")

    fields = multipart_fields(requests_mock.last_request)
    assert fields["user_fields_only"] == b"1"
    assert fields["upload"].decode() == "user_id,user_customfield1\r\n5,yes\r\n"


def test_table_split(ak):
    test1 = Table([("x", "y", "z"), ("a", "b", ""), ("1", "", "3"), ("4", "", "6")])
    tables = ak._split_tables_no_empties(test1, True, [])
    assert len(tables) == 2
    assert_matching_tables(tables[0], Table([("x", "y"), ("a", "b")]))
    assert_matching_tables(tables[1], Table([("x", "z"), ("1", "3"), ("4", "6")]))

    test2 = Table([("x", "y", "z"), ("a", "b", "c"), ("1", "2", "3"), ("4", "5", "6")])
    tables2 = ak._split_tables_no_empties(test2, True, [])
    assert len(tables2) == 1
    assert_matching_tables(tables2[0], test2)

    test3 = Table([("x", "y", "z"), ("a", "b", ""), ("1", "2", "3"), ("4", "5", "6")])
    tables3 = ak._split_tables_no_empties(test3, False, ["z"])
    assert len(tables3) == 2
    assert_matching_tables(tables3[0], Table([("x", "y"), ("a", "b")]))
    assert_matching_tables(tables3[1], Table([("x", "y", "z"), ("1", "2", "3"), ("4", "5", "6")]))


def test_collect_errors(ak, requests_mock):
    requests_mock.get(f"{BASE}/upload/12345/", json={"is_completed": True, "has_errors": 25})
    requests_mock.get(f"{BASE}/uploaderror/", json={"meta": {"next": ""}, "objects": []})

    ak.collect_upload_errors([{"id": "12345"}])

    # The upload's status is polled, then its errors are paged 20 at a time. With 25
    # errors that is two pages (offsets 0 and 20) and no third page.
    error_requests = [r for r in requests_mock.request_history if "uploaderror" in r.url]
    assert [query(r)["_offset"] for r in error_requests] == [["0"], ["20"]]
    assert requests_mock.request_history[0].url == f"{BASE}/upload/12345/"
