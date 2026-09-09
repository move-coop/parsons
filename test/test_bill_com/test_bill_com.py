import json
import unittest

import requests_mock

from parsons import BillCom, Table
from test.conftest import assert_matching_tables


class TestBillCom(unittest.TestCase):
    @requests_mock.Mocker()
    def setUp(self, m):
        self.api_url = "http://FAKEURL.com/"

        m.post(
            self.api_url + "Login.json",
            text=json.dumps({"response_data": {"sessionId": "FAKE"}}),
        )
        self.bc = BillCom("FAKE", "FAKE", "FAKE", "FAKE", self.api_url)

        self.fake_time = "2019-02-29T00:00:00.000+0000"
        self.fake_date = "2019-02-29"
        self.fake_customer_email = "fake_customer_email@fake_customer_email.com"

        self.fake_user_list = {
            "response_status": 0,
            "response_message": "Success",
            "response_data": [
                {
                    "entity": "User",
                    "id": "fake_user_id",
                    "isActive": "1",
                    "createdTime": self.fake_time,
                    "updatedTime": self.fake_time,
                    "loginId": "fake_login_id",
                    "profileId": "fake_profile_id",
                    "firstName": "fake_first_name",
                    "lastName": "fake_last_name",
                    "email": "fake_email@fake_email.com",
                    "timezoneId": "7",
                    "partnerUserGroupType": "2",
                }
            ],
        }

        self.fake_customer_list = {
            "response_status": 0,
            "response_message": "Success",
            "response_data": [
                {
                    "entity": "Customer",
                    "id": "fake_customer_id",
                    "isActive": "1",
                    "createdTime": self.fake_time,
                    "updatedTime": self.fake_time,
                    "name": "fake_customer_name",
                    "shortName": "fake_shorter_customer_name",
                    "parentCustomerId": "0",
                    "companyName": "fake_company_name",
                    "contactFirstName": "fake_first_name",
                    "contactLastName": "fake_last_name",
                    "accNumber": "0",
                    "billAddress1": "123 Fake Street",
                    "billAddress2": "Suite 13",
                    "billAddress3": None,
                    "billAddress4": None,
                    "billAddressCity": "Fake City",
                    "billAddressState": "FS",
                    "billAddressCountry": "USA",
                    "billAddressZip": "11111",
                    "shipAddress1": "123 Fake Street",
                    "shipAddress2": "Office 13",
                    "shipAddress3": None,
                    "shipAddress4": None,
                    "shipAddressCity": "Fake City",
                    "shipAddressState": "FS",
                    "shipAddressCountry": "USA",
                    "shipAddressZip": "11111",
                    "email": self.fake_customer_email,
                    "phone": "123-123-1234",
                    "altPhone": "123-123-1256",
                    "fax": "123-123-1235",
                    "description": "fake_description",
                    "printAs": None,
                    "mergedIntoId": "0",
                    "hasAuthorizedToCharge": False,
                    "accountType": "1",
                }
            ],
        }

        self.fake_customer_read_json = {
            "response_status": 0,
            "response_message": "Success",
            "response_data": self.fake_customer_list["response_data"][0],
        }

        self.fake_invoice_list = {
            "response_status": 0,
            "response_message": "Success",
            "response_data": [
                {
                    "entity": "Invoice",
                    "id": "fake_invoice_id",
                    "isActive": "1",
                    "createdTime": self.fake_time,
                    "updatedTime": self.fake_time,
                    "customerId": "fake_customer_id",
                    "invoiceNumber": "fake_invoice_number",
                    "invoiceDate": self.fake_date,
                    "dueDate": self.fake_date,
                    "glPostingDate": self.fake_date,
                    "amount": 1.0,
                    "amountDue": 1.0,
                    "paymentStatus": "1",
                    "description": None,
                    "poNumber": None,
                    "isToBePrinted": False,
                    "isToBeEmailed": False,
                    "lastSentTime": None,
                    "itemSalesTax": "0",
                    "salesTaxPercentage": 0,
                    "salesTaxTotal": 0.0,
                    "terms": None,
                    "salesRep": None,
                    "FOB": None,
                    "shipDate": None,
                    "shipMethod": None,
                    "departmentId": "0",
                    "locationId": "0",
                    "actgClassId": "0",
                    "jobId": "0",
                    "payToBankAccountId": "0",
                    "payToChartOfAccountId": "0",
                    "invoiceTemplateId": "0",
                    "hasAutoPay": False,
                    "source": "0",
                    "emailDeliveryOption": "1",
                    "mailDeliveryOption": "0",
                    "creditAmount": 0.0,
                    "invoiceLineItems": [
                        {
                            "entity": "InvoiceLineItem",
                            "id": "fake_line_item_id",
                            "createdTime": self.fake_time,
                            "updatedTime": self.fake_time,
                            "invoiceId": "fake_invoice_id",
                            "itemId": "0",
                            "quantity": 1,
                            "amount": 1.0,
                            "price": None,
                            "serviceDate": None,
                            "ratePercent": None,
                            "chartOfAccountId": "0",
                            "departmentId": "0",
                            "locationId": "0",
                            "actgClassId": "0",
                            "jobId": "0",
                            "description": None,
                            "taxable": False,
                            "taxCode": "Non",
                        }
                    ],
                }
            ],
        }

        self.fake_invoice_read_json = {
            "response_status": 0,
            "response_message": "Success",
            "response_data": self.fake_invoice_list["response_data"][0],
        }

        self.fake_invoice_line_items = self.fake_invoice_list["response_data"][0][
            "invoiceLineItems"
        ]

    def test_init(self):
        assert self.bc.session_id == "FAKE"

    def test_get_payload(self):
        fake_json = {"fake_key": "fake_data"}
        payload = self.bc._get_payload(fake_json)
        assert payload == {
            "devKey": self.bc.dev_key,
            "sessionId": self.bc.session_id,
            "data": json.dumps(fake_json),
        }

    @requests_mock.Mocker()
    def test_post_request(self, m):
        data = {"id": "fake_customer_id"}
        m.post(
            self.api_url + "Crud/Read/Customer.json",
            text=json.dumps(self.fake_customer_read_json),
        )
        assert self.bc._post_request(data, "Read", "Customer") == self.fake_customer_read_json

    def paginate_callback(self, request, context):
        # Internal method for simulating pagination

        remainder = [
            {"dict": 2, "col": "C"},
            {"dict": 3, "col": "D"},
            {"dict": 4, "col": "E"},
        ]

        return {"response_data": remainder}

    @requests_mock.Mocker()
    def test_paginate_list(self, m):
        r = [{"dict": 0, "col": "A"}, {"dict": 1, "col": "B"}]

        overflow = [
            {"dict": 2, "col": "C"},
            {"dict": 3, "col": "D"},
            {"dict": 4, "col": "E"},
        ]

        r_table = Table()
        r_table.concat(Table(r))
        r_table.concat(Table(overflow))

        data = {"start": 0, "max": 2}

        object_name = "Listme"

        m.post(self.api_url + f"List/{object_name}.json", json=self.paginate_callback)
        assert_matching_tables(self.bc._paginate_list(r, data, object_name), r_table)

    @requests_mock.Mocker()
    def test_get_request_response(self, m):
        data = {"id": "fake_customer_id"}
        m.post(
            self.api_url + "Crud/Read/Customer.json",
            text=json.dumps(self.fake_customer_read_json),
        )
        assert (
            self.bc._get_request_response(data, "Read", "Customer", "response_data")
            == self.fake_customer_read_json["response_data"]
        )

    @requests_mock.Mocker()
    def test_get_user_list(self, m):
        m.post(self.api_url + "List/User.json", text=json.dumps(self.fake_user_list))
        assert_matching_tables(self.bc.get_user_list(), Table(self.fake_user_list["response_data"]))

    @requests_mock.Mocker()
    def test_get_customer_list(self, m):
        m.post(
            self.api_url + "List/Customer.json",
            text=json.dumps(self.fake_customer_list),
        )
        assert_matching_tables(
            self.bc.get_customer_list(), Table(self.fake_customer_list["response_data"])
        )

    @requests_mock.Mocker()
    def test_get_invoice_list(self, m):
        m.post(self.api_url + "List/Invoice.json", text=json.dumps(self.fake_invoice_list))
        assert_matching_tables(
            self.bc.get_invoice_list(), Table(self.fake_invoice_list["response_data"])
        )

    @requests_mock.Mocker()
    def test_read_customer(self, m):
        m.post(
            self.api_url + "Crud/Read/Customer.json",
            text=json.dumps(self.fake_customer_read_json),
        )
        assert (
            self.bc.read_customer("fake_customer_id")
            == self.fake_customer_read_json["response_data"]
        )

    @requests_mock.Mocker()
    def test_read_invoice(self, m):
        m.post(
            self.api_url + "Crud/Read/Invoice.json",
            text=json.dumps(self.fake_invoice_read_json),
        )
        assert (
            self.bc.read_invoice("fake_invoice_id") == self.fake_invoice_read_json["response_data"]
        )

    def test_check_customer(self):
        assert self.bc.check_customer({"id": "fake_customer_id"}, {"id": "fake_customer_id"})
        assert self.bc.check_customer(
            {"email": "fake_email@fake_email.com"},
            {"id": "fake_customer_id", "email": "fake_email@fake_email.com"},
        )
        assert not self.bc.check_customer({"id": "fake_customer_id1"}, {"id": "fake_customer_id2"})
        assert not self.bc.check_customer(
            {"email": "fake_email1@fake_email.com"},
            {"id": "fake_customer_id2", "email": "fake_email2@fake_email.com"},
        )

    @requests_mock.Mocker()
    def test_get_or_create_customer(self, m):
        m.post(
            self.api_url + "List/Customer.json",
            text=json.dumps(self.fake_customer_list),
        )
        m.post(
            self.api_url + "Crud/Create/Customer.json",
            text=json.dumps(self.fake_customer_read_json),
        )
        assert (
            self.bc.get_or_create_customer("fake_customer_name", self.fake_customer_email)
            == self.fake_customer_read_json["response_data"]
        )

    @requests_mock.Mocker()
    def test_create_invoice(self, m):
        m.post(
            self.api_url + "Crud/Create/Invoice.json",
            text=json.dumps(self.fake_invoice_read_json),
        )
        assert (
            self.bc.create_invoice(
                "fake_customer_id",
                "1",
                self.fake_date,
                self.fake_date,
                self.fake_invoice_line_items,
            )
            == self.fake_invoice_read_json["response_data"]
        )

    @requests_mock.Mocker()
    def test_send_invoice(self, m):
        send_invoice_response_json = {
            "response_status": 0,
            "response_message": "Success",
            "response_data": {},
        }
        m.post(
            self.api_url + "SendInvoice.json",
            text=json.dumps(send_invoice_response_json),
        )
        assert (
            self.bc.send_invoice(
                "fake_invoice_id",
                "fake_user_id",
                "fake_user_email@fake_email.com",
                "fake_subject",
                "fake_message_body",
            )
            == {}
        )
