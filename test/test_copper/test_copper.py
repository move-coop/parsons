"""Tests for the Copper connector.

Copper talks to the ProsperWorks/Copper REST API via ``requests`` directly, so we
mock at the HTTP boundary with the ``requests_mock`` fixture and let the real
connector code (URL building, headers, pagination, unpacking) run against it.
Canned API responses live in ``data/`` and are loaded with the ``load`` fixture.
"""

import json

import pytest

from parsons import Table
from test.conftest import assert_matching_tables


def _paginated(payload):
    """Build a ``requests_mock`` ``json=`` callback that serves ``payload`` the way
    Copper's API does.

    For list responses it slices out the requested page and advertises the total
    row count via the ``X-Pw-Total`` header, which is how ``paginate_request`` learns
    how many pages to fetch. GET endpoints (custom fields, activity/contact types)
    carry no request body and are returned whole on a single page.
    """

    def callback(request, context):
        context.status_code = 200
        if request.text is None:  # GET requests carry no body -> single page
            start, finish = 0, 100
        else:
            body = json.loads(request.text)
            start = (body["page_number"] - 1) * body["page_size"]
            finish = start + body["page_size"]
        if isinstance(payload, list):
            context.headers["X-Pw-Total"] = str(len(payload))
            return payload[start:finish]
        return payload

    return callback


def _table_named(tables, name):
    """Pull the Parsons Table labeled ``name`` out of Copper's list-of-dicts output."""
    return next(t["tbl"] for t in tables if t["name"] == name)


# --- Shared expected output (reused across the get_standard_object / get_people /
# get_custom_fields tests, which exercise the same processing on the same data). ---

PROCESSED_PEOPLE = [
    {
        "id": 78757050,
        "name": "Person One",
        "prefix": None,
        "first_name": "Person",
        "middle_name": None,
        "last_name": "One",
        "suffix": None,
        "assignee_id": None,
        "company_id": 12030795,
        "company_name": "Indivisible CityA",
        "contact_type_id": 501950,
        "details": None,
        "tags": [],
        "title": None,
        "date_created": 1558169903,
        "date_modified": 1558169910,
        "date_last_contacted": 1558169891,
        "interaction_count": 1,
        "leads_converted_from": [],
        "date_lead_created": None,
        "address_city": "CityA",
        "address_country": None,
        "address_postal_code": "12345",
        "address_state": "StateI",
        "address_street": None,
    },
    {
        "id": 78477076,
        "name": "Person Two",
        "prefix": None,
        "first_name": "Person",
        "middle_name": None,
        "last_name": "Two",
        "suffix": None,
        "assignee_id": 289533,
        "company_id": 12096071,
        "company_name": "Indivisible StateII",
        "contact_type_id": 501950,
        "details": None,
        "tags": ["treasurer"],
        "title": "Treasurer",
        "date_created": 1557761054,
        "date_modified": 1558218799,
        "date_last_contacted": 1558196341,
        "interaction_count": 14,
        "leads_converted_from": [],
        "date_lead_created": None,
        "address_city": None,
        "address_country": None,
        "address_postal_code": None,
        "address_state": None,
        "address_street": None,
    },
    {
        "id": 78839154,
        "name": "Person Three",
        "prefix": None,
        "first_name": "Person",
        "middle_name": None,
        "last_name": "Three",
        "suffix": None,
        "assignee_id": None,
        "company_id": 34966944,
        "company_name": "Flip StateIII",
        "contact_type_id": 501950,
        "details": None,
        "tags": [],
        "title": None,
        "date_created": 1558223367,
        "date_modified": 1558223494,
        "date_last_contacted": 1558223356,
        "interaction_count": 2,
        "leads_converted_from": [],
        "date_lead_created": None,
        "address_city": "CityC",
        "address_country": None,
        "address_postal_code": "54321",
        "address_state": "StateIII",
        "address_street": None,
    },
]

PROCESSED_PEOPLE_EMAILS = [
    {"id": 78757050, "emails_category": "work", "emails_email": "PersonOne@fakemail.nope"},
    {"id": 78477076, "emails_category": "work", "emails_email": "Personb23@gmail.com"},
    {"id": 78839154, "emails_category": "work", "emails_email": "Person.Three@fakemail.nope"},
]

CUSTOM_FIELD_TABLE_NAMES = [
    "custom_fields",
    "custom_fields_available",
    "custom_fields_options",
]

CUSTOM_FIELD_TABLES = {
    "custom_fields": [
        {"id": 101674, "name": "Event Date", "data_type": "Date"},
        {"id": 102127, "name": "Date Added", "data_type": "Date"},
        {"id": 109116, "name": "Local Group Subtype", "data_type": "Dropdown"},
    ],
    "custom_fields_available": [
        {"id": 101674, "available_on": "opportunity"},
        {"id": 102127, "available_on": "company"},
        {"id": 102127, "available_on": "person"},
        {"id": 109116, "available_on": "company"},
    ],
    "custom_fields_options": [
        {
            "id": 109116,
            "name": "Local Group Subtype",
            "options_id": 140251,
            "options_name": "Public (displayed in map)",
            "options_rank": 0,
        },
        {
            "id": 109116,
            "name": "Local Group Subtype",
            "options_id": 140250,
            "options_name": "New (Needs Processing)",
            "options_rank": 4,
        },
        {
            "id": 109116,
            "name": "Local Group Subtype",
            "options_id": 140252,
            "options_name": "Private (not on map)",
            "options_rank": 1,
        },
        {
            "id": 109116,
            "name": "Local Group Subtype",
            "options_id": 140254,
            "options_name": "National",
            "options_rank": 5,
        },
        {
            "id": 109116,
            "name": "Local Group Subtype",
            "options_id": 140766,
            "options_name": "Not following principles",
            "options_rank": 3,
        },
        {
            "id": 109116,
            "name": "Local Group Subtype",
            "options_id": 140764,
            "options_name": "International",
            "options_rank": 6,
        },
        {
            "id": 109116,
            "name": "Local Group Subtype",
            "options_id": 141434,
            "options_name": "Inactive",
            "options_rank": 2,
        },
    ],
}


def test_init(copper):
    assert copper.user_email == "usr@losr.fake"
    assert copper.api_key == "key"


def test_base_request(copper, requests_mock):
    fake_search = [{"id": "fake"}]
    requests_mock.post(copper.uri + "/people/search", json=fake_search)

    resp = copper.base_request("/people/search", req_type="POST")

    assert resp.json() == fake_search
    # POST requests default to the first page of 200 rows.
    assert requests_mock.last_request.json() == {"page_number": 1, "page_size": 200}


def test_base_request_sends_auth_headers(copper, requests_mock):
    # Copper authenticates through headers (HTTPBasicAuth does not work for its API).
    requests_mock.post(copper.uri + "/people/search", json=[])

    copper.base_request("/people/search", req_type="POST")

    headers = requests_mock.last_request.headers
    assert headers["X-PW-AccessToken"] == "key"
    assert headers["X-PW-UserEmail"] == "usr@losr.fake"
    assert headers["X-PW-Application"] == "developer_api"


def test_base_request_post_sends_paging_and_filters(copper, requests_mock):
    # POST requests carry page_number/page_size plus any caller filters in the body.
    requests_mock.post(copper.uri + "/people/search", json=[])

    copper.base_request(
        "/people/search", req_type="POST", page=3, page_size=25, filters={"name": "Person"}
    )

    assert requests_mock.last_request.json() == {
        "name": "Person",
        "page_number": 3,
        "page_size": 25,
    }


def test_base_request_get_sends_filters_as_params(copper, requests_mock):
    # GET requests must not send a body (that would be malformed); filters go in the
    # query string instead (the connector json.dumps() the payload into params).
    requests_mock.get(copper.uri + "/custom_field_definitions/", json=[])

    copper.base_request("/custom_field_definitions/", req_type="GET", filters={"foo": "bar"})

    req = requests_mock.last_request
    assert req.text is None
    assert "foo" in req.url
    assert "bar" in req.url


@pytest.mark.parametrize("page_size", [1, 2])
def test_paginate_request_reassembles_pages(copper, requests_mock, load, page_size):
    people = load("people_search")
    requests_mock.post(copper.uri + "/people/search", json=_paginated(people))

    # page_size=1 forces one row per page; page_size=2 does not divide the 3 rows,
    # exercising the ceil() page-count math. Either way paginate_request must
    # reassemble every row, in order, into the full result set.
    result = copper.paginate_request("/people/search", page_size=page_size, req_type="POST")

    assert_matching_tables(Table(people), Table(result))


def test_paginate_request_defaults_to_200_page_size(copper, requests_mock, load):
    requests_mock.post(copper.uri + "/people/search", json=_paginated(load("people_search")))

    copper.paginate_request("/people/search", req_type="POST")

    assert requests_mock.last_request.json()["page_size"] == 200


@pytest.mark.parametrize("page_number", [1, 2, 3])
def test_paginate_request_single_page_via_filter(copper, requests_mock, load, page_number):
    people = load("people_search")
    requests_mock.post(copper.uri + "/people/search", json=_paginated(people))

    # Pinning page_number in filters fetches exactly that one page and nothing else
    # (page_size=1, so each page is a single row).
    result = copper.paginate_request(
        "/people/search", page_size=1, req_type="POST", filters={"page_number": page_number}
    )

    assert Table(result).num_rows == 1
    assert result[0]["id"] == people[page_number - 1]["id"]


def test_paginate_request_empty_response(copper, requests_mock):
    requests_mock.post(copper.uri + "/people/search", text="")

    assert copper.paginate_request("/people/search", req_type="POST") == []


def test_process_json(copper):
    # Stress-testing the combination of unpack methods with a contrived table from hell.
    fake_response = [
        {
            "id": 1,
            "Simple List Col": ["one", "two", "three"],
            "Mixed List Col": [None, 2, "three"],
            "Spotty List Col": [1, 2, 3],
            "Multidim List Col": [[1, 2], [None, "two"], []],
            "Nested List Col": [
                {"A": 1, "B": "one"},
                {"A": 2, "B": "two"},
                {"A": 3, "B": "three"},
            ],
            "Simple Dict Col": {"one": 1, "two": 2, "three": 3},
            "Nested Dict Col": {"A": 1, "B": ["two", 2], "C": [None, 3, "three"]},
        },
        {
            "id": 2,
            "Simple List Col": ["four", "five", "six"],
            "Mixed List Col": ["four", None, 6],
            "Spotty List Col": [],
            "Multidim List Col": [[3, None], [], ["three", "four"]],
            "Nested List Col": [
                {"A": 4, "B": "four"},
                {"A": 5, "B": "five"},
                {"A": 6, "B": "six"},
            ],
            "Simple Dict Col": {"one": "I", "two": "II", "three": "III"},
            "Nested Dict Col": {"A": ["one"], "B": [], "C": 3},
        },
        {
            "id": 3,
            "Simple List Col": ["seven", "eight", "nine"],
            "Mixed List Col": [7, "eight", None],
            "Spotty List Col": None,
            "Multidim List Col": [["five", 6], [None]],
            "Nested List Col": [
                {"A": 7, "B": "seven"},
                {"A": 8, "B": "eight"},
                {"A": 9, "B": "nine"},
            ],
            "Simple Dict Col": {"one": "x", "two": "xx", "three": "xxx"},
            "Nested Dict Col": {"A": None, "B": 2, "C": [None, 3, "three"]},
        },
    ]

    table_names = ["fake_Nested List Col", "fake"]
    expected_nested = [
        {"id": 1, "Nested List Col_A": 1, "Nested List Col_B": "one"},
        {"id": 1, "Nested List Col_A": 2, "Nested List Col_B": "two"},
        {"id": 1, "Nested List Col_A": 3, "Nested List Col_B": "three"},
        {"id": 2, "Nested List Col_A": 4, "Nested List Col_B": "four"},
        {"id": 2, "Nested List Col_A": 5, "Nested List Col_B": "five"},
        {"id": 2, "Nested List Col_A": 6, "Nested List Col_B": "six"},
        {"id": 3, "Nested List Col_A": 7, "Nested List Col_B": "seven"},
        {"id": 3, "Nested List Col_A": 8, "Nested List Col_B": "eight"},
        {"id": 3, "Nested List Col_A": 9, "Nested List Col_B": "nine"},
    ]
    expected_fake = [
        {
            "id": 1,
            "Simple List Col": ["one", "two", "three"],
            "Mixed List Col": [None, 2, "three"],
            "Spotty List Col": [1, 2, 3],
            "Multidim List Col": [[1, 2], [None, "two"], []],
            "Simple Dict Col_one": 1,
            "Simple Dict Col_three": 3,
            "Simple Dict Col_two": 2,
            "Nested Dict Col_A": 1,
            "Nested Dict Col_B": ["two", 2],
            "Nested Dict Col_C": [None, 3, "three"],
        },
        {
            "id": 2,
            "Simple List Col": ["four", "five", "six"],
            "Mixed List Col": ["four", None, 6],
            "Spotty List Col": [],
            "Multidim List Col": [[3, None], [], ["three", "four"]],
            "Simple Dict Col_one": "I",
            "Simple Dict Col_three": "III",
            "Simple Dict Col_two": "II",
            "Nested Dict Col_A": ["one"],
            "Nested Dict Col_B": [],
            "Nested Dict Col_C": 3,
        },
        {
            "id": 3,
            "Simple List Col": ["seven", "eight", "nine"],
            "Mixed List Col": [7, "eight", None],
            "Spotty List Col": [None],
            "Multidim List Col": [["five", 6], [None]],
            "Simple Dict Col_one": "x",
            "Simple Dict Col_three": "xxx",
            "Simple Dict Col_two": "xx",
            "Nested Dict Col_A": None,
            "Nested Dict Col_B": 2,
            "Nested Dict Col_C": [None, 3, "three"],
        },
    ]
    expected = {"fake_Nested List Col": expected_nested, "fake": expected_fake}

    from parsons import Copper

    copper = Copper("usr@losr.fake", "key")

    fake_processed = copper.process_json(fake_response, "fake")
    assert [f["name"] for f in fake_processed] == table_names
    for name in table_names:
        assert_matching_tables(Table(expected[name]), _table_named(fake_processed, name))

    # tidy=0 unpacks every nested column into its own table (one per packed column).
    fake_tidy = copper.process_json(fake_response, "fake", tidy=0)
    assert len(fake_tidy) == len(fake_response[0]) - 1


def test_process_custom_fields(copper, load):
    # The same fixture drives both process_custom_fields() and get_custom_fields().
    fake_processed = copper.process_custom_fields(load("custom_fields_search"))

    assert [f["name"] for f in fake_processed] == CUSTOM_FIELD_TABLE_NAMES
    for name in CUSTOM_FIELD_TABLE_NAMES:
        assert_matching_tables(Table(CUSTOM_FIELD_TABLES[name]), _table_named(fake_processed, name))


def test_get_standard_object(copper, requests_mock, load):
    requests_mock.post(copper.uri + "/people/search", json=_paginated(load("people_search")))

    processed = copper.get_standard_object("people")

    assert_matching_tables(Table(PROCESSED_PEOPLE), _table_named(processed, "people"))
    assert_matching_tables(Table(PROCESSED_PEOPLE_EMAILS), _table_named(processed, "people_emails"))


def test_get_people(copper, requests_mock, load):
    requests_mock.post(copper.uri + "/people/search", json=_paginated(load("people_search")))

    processed = copper.get_people()

    # Dicts & simple lists are unpacked to columns on the original table (people);
    # lists of dicts (emails) are unpacked into their own long table.
    assert_matching_tables(Table(PROCESSED_PEOPLE), _table_named(processed, "people"))
    assert_matching_tables(Table(PROCESSED_PEOPLE_EMAILS), _table_named(processed, "people_emails"))


def test_get_opportunities(copper, requests_mock, load):
    processed_opps = [
        {
            "id": 14340759,
            "name": "Company1",
            "assignee_id": 659394,
            "close_date": None,
            "company_id": 29324143,
            "company_name": "Company1",
            "customer_source_id": None,
            "details": None,
            "loss_reason_id": None,
            "pipeline_id": 489028,
            "pipeline_stage_id": 2529569,
            "primary_contact_id": 67747998,
            "priority": "High",
            "status": "Open",
            "tags": ["opportunities import-1540158946352"],
            "interaction_count": 0,
            "monetary_unit": "USD",
            "monetary_value": 100000.0,
            "converted_unit": None,
            "converted_value": None,
            "win_probability": None,
            "date_stage_changed": 1548866182,
            "date_last_contacted": None,
            "leads_converted_from": [],
            "date_lead_created": None,
            "date_created": 1540159060,
            "date_modified": 1550858334,
        },
        {
            "id": 14161592,
            "name": "Company2",
            "assignee_id": 659394,
            "close_date": "11/10/2018",
            "company_id": 28729196,
            "company_name": "Company2",
            "customer_source_id": None,
            "details": None,
            "loss_reason_id": None,
            "pipeline_id": 531482,
            "pipeline_stage_id": 2607171,
            "primary_contact_id": 67243374,
            "priority": "High",
            "status": "Open",
            "tags": [],
            "interaction_count": 36,
            "monetary_unit": "USD",
            "monetary_value": 77000.0,
            "converted_unit": None,
            "converted_value": None,
            "win_probability": None,
            "date_stage_changed": 1551191957,
            "date_last_contacted": 1552339800,
            "leads_converted_from": [],
            "date_lead_created": None,
            "date_created": 1539192375,
            "date_modified": 1552340016,
        },
        {
            "id": 14286548,
            "name": "Company3",
            "assignee_id": 644608,
            "close_date": "11/18/2018",
            "company_id": 29492294,
            "company_name": "Company3",
            "customer_source_id": None,
            "details": None,
            "loss_reason_id": None,
            "pipeline_id": 531482,
            "pipeline_stage_id": 2482007,
            "primary_contact_id": 67637400,
            "priority": "None",
            "status": "Open",
            "tags": [],
            "interaction_count": 19,
            "monetary_unit": "USD",
            "monetary_value": 150000.0,
            "converted_unit": None,
            "converted_value": None,
            "win_probability": 0,
            "date_stage_changed": 1539870749,
            "date_last_contacted": 1555534313,
            "leads_converted_from": [],
            "date_lead_created": None,
            "date_created": 1539870749,
            "date_modified": 1555550658,
        },
    ]

    processed_opps_cf = [
        {
            "id": 14340759,
            "custom_fields_custom_field_definition_id": 272931,
            "custom_fields_value": [],
        },
        {
            "id": 14340759,
            "custom_fields_custom_field_definition_id": 272927,
            "custom_fields_value": None,
        },
        {
            "id": 14161592,
            "custom_fields_custom_field_definition_id": 272931,
            "custom_fields_value": [],
        },
        {
            "id": 14161592,
            "custom_fields_custom_field_definition_id": 272927,
            "custom_fields_value": None,
        },
        {
            "id": 14286548,
            "custom_fields_custom_field_definition_id": 272931,
            "custom_fields_value": [],
        },
        {
            "id": 14286548,
            "custom_fields_custom_field_definition_id": 272927,
            "custom_fields_value": None,
        },
    ]

    requests_mock.post(
        copper.uri + "/opportunities/search", json=_paginated(load("opportunities_search"))
    )

    processed = copper.get_opportunities()

    assert_matching_tables(Table(processed_opps), _table_named(processed, "opportunities"))
    assert_matching_tables(
        Table(processed_opps_cf), _table_named(processed, "opportunities_custom_fields")
    )


def test_get_companies(copper, requests_mock, load):
    processed_companies = [
        {
            "id": 35015567,
            "name": "Company One",
            "assignee_id": None,
            "contact_type_id": 547508,
            "details": None,
            "email_domain": "companyone@fake.nope",
            "tags": [],
            "interaction_count": 1,
            "date_created": 1558441519,
            "date_modified": 1558441535,
            "address_city": "CityA",
            "address_country": None,
            "address_postal_code": "12345",
            "address_state": "New York",
            "address_street": None,
        },
        {
            "id": 35026533,
            "name": "Company Two",
            "assignee_id": None,
            "contact_type_id": 547508,
            "details": None,
            "email_domain": "companytwo@fake.nope",
            "tags": [],
            "interaction_count": 1,
            "date_created": 1558452953,
            "date_modified": 1558452967,
            "address_city": "CityB",
            "address_country": None,
            "address_postal_code": "23451",
            "address_state": "New York",
            "address_street": None,
        },
        {
            "id": 35014973,
            "name": "Company Three",
            "assignee_id": None,
            "contact_type_id": 547508,
            "details": None,
            "email_domain": None,
            "tags": [],
            "interaction_count": 1,
            "date_created": 1558434147,
            "date_modified": 1558458137,
            "address_city": None,
            "address_country": None,
            "address_postal_code": "34512",
            "address_state": "Alabama",
            "address_street": None,
        },
        {
            "id": 35029116,
            "name": "Company Four",
            "assignee_id": None,
            "contact_type_id": 547508,
            "details": None,
            "email_domain": "companyfour@fake.nope",
            "tags": [],
            "interaction_count": 0,
            "date_created": 1558461301,
            "date_modified": 1558461301,
            "address_city": "CityD ",
            "address_country": None,
            "address_postal_code": "45123",
            "address_state": "California",
            "address_street": None,
        },
        {
            "id": 35082308,
            "name": "Company Five",
            "assignee_id": None,
            "contact_type_id": 547508,
            "details": None,
            "email_domain": "companyfive@fake.nope",
            "tags": [],
            "interaction_count": 1,
            "date_created": 1558639445,
            "date_modified": 1558639459,
            "address_city": "CityE",
            "address_country": None,
            "address_postal_code": "51234",
            "address_state": "Arizona",
            "address_street": None,
        },
    ]

    processed_companies_phones = [
        {"id": 35082308, "phone_numbers_category": "work", "phone_numbers_number": "123-555-9876"}
    ]

    requests_mock.post(copper.uri + "/companies/search", json=_paginated(load("companies_search")))

    processed = copper.get_companies()

    assert_matching_tables(Table(processed_companies), _table_named(processed, "companies"))
    assert_matching_tables(
        Table(processed_companies_phones), _table_named(processed, "companies_phone_numbers")
    )


def test_get_activities(copper, requests_mock, load):
    processed_activities = [
        {
            "id": 5369412841,
            "user_id": 289533,
            "details": None,
            "activity_date": 1554149472,
            "old_value": None,
            "new_value": None,
            "date_created": 1554149472,
            "date_modified": 1554149472,
            "parent_id": 76469872,
            "parent_type": "person",
            "type_category": "system",
            "type_id": 1,
        },
        {
            "id": 5223481640,
            "user_id": 377343,
            "details": None,
            "activity_date": 1550789277,
            "old_value": None,
            "new_value": None,
            "date_created": 1550789277,
            "date_modified": 1550789277,
            "parent_id": 28465522,
            "parent_type": "person",
            "type_category": "system",
            "type_id": 1,
        },
        {
            "id": 5185524266,
            "user_id": 703426,
            "details": None,
            "activity_date": 1549983210,
            "old_value": None,
            "new_value": None,
            "date_created": 1549983210,
            "date_modified": 1549983210,
            "parent_id": 12035585,
            "parent_type": "company",
            "type_category": "system",
            "type_id": 1,
        },
    ]

    requests_mock.post(
        copper.uri + "/activities/search", json=_paginated(load("activities_search"))
    )

    processed = copper.get_activities()

    # No nested columns in activities -> a single table.
    assert_matching_tables(Table(processed_activities), processed[0]["tbl"])


def test_get_custom_fields(copper, requests_mock, load):
    requests_mock.get(
        copper.uri + "/custom_field_definitions/",
        json=_paginated(load("custom_fields_search")),
    )

    processed = copper.get_custom_fields()

    assert [f["name"] for f in processed] == CUSTOM_FIELD_TABLE_NAMES
    for name in CUSTOM_FIELD_TABLE_NAMES:
        assert_matching_tables(Table(CUSTOM_FIELD_TABLES[name]), _table_named(processed, name))


def test_get_activity_types(copper, requests_mock, load):
    processed_at = [
        {
            "category": "system",
            "count_as_interaction": False,
            "id": 1,
            "is_disabled": False,
            "name": "Property Changed",
        },
        {
            "category": "system",
            "count_as_interaction": False,
            "id": 3,
            "is_disabled": False,
            "name": "Pipeline Stage Changed",
        },
        {
            "category": "user",
            "count_as_interaction": False,
            "id": 0,
            "is_disabled": False,
            "name": "Note",
        },
        {
            "category": "user",
            "count_as_interaction": True,
            "id": 504464,
            "is_disabled": False,
            "name": "Mail",
        },
        {
            "category": "user",
            "count_as_interaction": True,
            "id": 248465,
            "is_disabled": False,
            "name": "Stories from the Field",
        },
        {
            "category": "user",
            "count_as_interaction": True,
            "id": 236962,
            "is_disabled": False,
            "name": "Press Coverage",
        },
    ]

    requests_mock.get(copper.uri + "/activity_types/", json=_paginated(load("activity_types_list")))

    processed = copper.get_activity_types()

    # No nested columns in activity types -> a single table (system rows then user rows).
    assert_matching_tables(Table(processed_at), processed[0]["tbl"])


def test_get_contact_types(copper, requests_mock, load):
    processed_ct = [
        {"id": 501947, "name": "Potential Customer"},
        {"id": 501948, "name": "Current Customer"},
        {"id": 501949, "name": "Uncategorized"},
        {"id": 501950, "name": "Group Leader"},
        {"id": 540331, "name": "Partner"},
        {"id": 540333, "name": "Funder"},
        {"id": 540334, "name": "Potential Funder"},
        {"id": 540335, "name": "Other"},
        {"id": 547508, "name": "Local Group"},
        {"id": 575833, "name": "Group Member"},
        {"id": 744795, "name": "Hill Contact"},
        {"id": 967249, "name": "State Leg Contact"},
    ]

    requests_mock.get(copper.uri + "/contact_types/", json=_paginated(load("contact_types_list")))

    processed = copper.get_contact_types()

    assert_matching_tables(Table(processed_ct), processed)
