"""Tests for the Bill.com connector."""

import json

from parsons import Table
from test.conftest import assert_matching_tables

FAKE_DATE = "2019-02-29"
FAKE_CUSTOMER_EMAIL = "fake_customer_email@fake_customer_email.com"


def test_get_payload(bc):
    payload = bc._get_payload({"fake_key": "fake_data"})

    assert payload == {
        "devKey": bc.dev_key,
        "sessionId": bc.session_id,
        "data": json.dumps({"fake_key": "fake_data"}),
    }


def test_post_request(bc, api_url, requests_mock, load):
    customer_read = load("customer_read")
    requests_mock.post(f"{api_url}Crud/Read/Customer.json", json=customer_read)

    assert bc._post_request({"id": "fake_customer_id"}, "Read", "Customer") == customer_read


def test_paginate_list(bc, api_url, requests_mock):
    first_page = [{"dict": 0, "col": "A"}, {"dict": 1, "col": "B"}]
    remainder = [{"dict": 2, "col": "C"}, {"dict": 3, "col": "D"}, {"dict": 4, "col": "E"}]
    requests_mock.post(f"{api_url}List/Listme.json", json={"response_data": remainder})

    expected = Table()
    expected.concat(Table(first_page))
    expected.concat(Table(remainder))

    result = bc._paginate_list(first_page, {"start": 0, "max": 2}, "Listme")

    assert_matching_tables(result, expected)


def test_get_request_response(bc, api_url, requests_mock, load):
    customer_read = load("customer_read")
    requests_mock.post(f"{api_url}Crud/Read/Customer.json", json=customer_read)

    result = bc._get_request_response(
        {"id": "fake_customer_id"}, "Read", "Customer", "response_data"
    )

    assert result == customer_read["response_data"]


def test_get_user_list(bc, api_url, requests_mock, load):
    user_list = load("user_list")
    requests_mock.post(f"{api_url}List/User.json", json=user_list)

    assert_matching_tables(bc.get_user_list(), Table(user_list["response_data"]))


def test_get_customer_list(bc, api_url, requests_mock, load):
    customer_list = load("customer_list")
    requests_mock.post(f"{api_url}List/Customer.json", json=customer_list)

    assert_matching_tables(bc.get_customer_list(), Table(customer_list["response_data"]))


def test_get_invoice_list(bc, api_url, requests_mock, load):
    invoice_list = load("invoice_list")
    requests_mock.post(f"{api_url}List/Invoice.json", json=invoice_list)

    assert_matching_tables(bc.get_invoice_list(), Table(invoice_list["response_data"]))


def test_read_customer(bc, api_url, requests_mock, load):
    customer_read = load("customer_read")
    requests_mock.post(f"{api_url}Crud/Read/Customer.json", json=customer_read)

    assert bc.read_customer("fake_customer_id") == customer_read["response_data"]


def test_read_invoice(bc, api_url, requests_mock, load):
    invoice_read = load("invoice_read")
    requests_mock.post(f"{api_url}Crud/Read/Invoice.json", json=invoice_read)

    assert bc.read_invoice("fake_invoice_id") == invoice_read["response_data"]


def test_check_customer(bc):
    assert bc.check_customer({"id": "fake_customer_id"}, {"id": "fake_customer_id"})
    assert bc.check_customer(
        {"email": "fake_email@fake_email.com"},
        {"id": "fake_customer_id", "email": "fake_email@fake_email.com"},
    )
    assert not bc.check_customer({"id": "fake_customer_id1"}, {"id": "fake_customer_id2"})
    assert not bc.check_customer(
        {"email": "fake_email1@fake_email.com"},
        {"id": "fake_customer_id2", "email": "fake_email2@fake_email.com"},
    )


def test_get_or_create_customer(bc, api_url, requests_mock, load):
    customer_read = load("customer_read")
    requests_mock.post(f"{api_url}List/Customer.json", json=load("customer_list"))
    requests_mock.post(f"{api_url}Crud/Create/Customer.json", json=customer_read)

    result = bc.get_or_create_customer("fake_customer_name", FAKE_CUSTOMER_EMAIL)

    assert result == customer_read["response_data"]


def test_create_invoice(bc, api_url, requests_mock, load):
    invoice_read = load("invoice_read")
    requests_mock.post(f"{api_url}Crud/Create/Invoice.json", json=invoice_read)

    result = bc.create_invoice(
        "fake_customer_id", "1", FAKE_DATE, FAKE_DATE, load("invoice_line_items")
    )

    assert result == invoice_read["response_data"]


def test_send_invoice(bc, api_url, requests_mock):
    requests_mock.post(
        f"{api_url}SendInvoice.json",
        json={"response_status": 0, "response_message": "Success", "response_data": {}},
    )

    result = bc.send_invoice(
        "fake_invoice_id",
        "fake_user_id",
        "fake_user_email@fake_email.com",
        "fake_subject",
        "fake_message_body",
    )

    assert result == {}
