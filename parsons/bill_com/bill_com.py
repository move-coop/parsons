import requests
import json
from parsons import Table


class BillCom(object):
    """
    `Args:`
        user_name: str
            The Bill.com username
        password: str
            The Bill.com password
        org_id: str
            The Bill.com organization id
        dev_key: str
            The Bill.com dev key
        api_url:
            The Bill.com end point url
    """

    def __init__(self, user_name, password, org_id, dev_key, api_url):
        self.headers = {"Content-Type": "application/x-www-form-urlencoded"}
        params = {
            "userName": user_name,
            "password": password,
            "orgId": org_id,
            "devKey": dev_key,
        }
        response = requests.post(url="%sLogin.json" % api_url, data=params, headers=self.headers)
        self.dev_key = dev_key
        self.api_url = api_url
        self.session_id = response.json()["response_data"]["sessionId"]

    def _get_payload(self, data):
        """
        `Args:`
            data: dict
                A dictionary containing the payload to be sent in the request.
                The dev_key and sessionId should not be included as they are
                dealt with separately.

        `Returns:`
            A dictionary of the payload to be sent in the request with the
            dev_key and sessionId added.
        """
        return {
            "devKey": self.dev_key,
            "sessionId": self.session_id,
            "data": json.dumps(data),
        }

    def _post_request(self, data, action, object_name):
        """
        `Args:`
            data: dict
                A dictionary containing the payload to be sent in the request.
                The dev_key and sessionId should not be included as they are
                dealt with separately.
            action: str
                The action to be taken on the given object.
                Possible values are "List", "Read", "Create", and "Send".
            object_name: str
                The id of the object. Possible values are "User", "Customer", and "Invoice".

        `Returns:`
            A dictionary containing the JSON response from the post request.
        """

        if action == "Read":
            url = "%sCrud/%s/%s.json" % (self.api_url, action, object_name)
        elif action == "Create":
            data["obj"]["entity"] = object_name
            url = "%sCrud/%s/%s.json" % (self.api_url, action, object_name)
        elif action == "Send":
            url = "%s%s%s.json" % (self.api_url, action, object_name)
        else:
            url = "%s%s/%s.json" % (self.api_url, action, object_name)
        payload = self._get_payload(data)
        response = requests.post(url=url, data=payload, headers=self.headers)
        return response.json()

    def _get_request_response(self, data, action, object_name, field="response_data"):
        """
        `Args:`
            data: dict
                A dictionary containing the payload to be sent in the request.
                The dev_key and sessionId should not be included as they are
                dealt with separately.
            action: str
                The action to be taken on the given object.
                Possible values are "List", "Read", "Create", and "Send".
            object_name: str
                The id of the object. Possible values are "User", "Customer", and "Invoice".
            field: str
                The JSON field where the response data is stored. Defaults to "response_data".

        `Returns:`
            A dictionary containing the choosen field from the JSON response from the post request.
        """
        r = self._post_request(data, action, object_name)[field]

        if action == "List":
            return self._paginate_list(r, data, object_name)

        return r

    def _paginate_list(self, response, data, object_name, field="response_data"):
        """
        Internal method to paginate through and concatenate results of lists larger than max
        `Args:`
            response: list of dicts
                Data from an initial list call
            data: dict
                Start, max, and kwargs from initial list call
            object_name: str
                Name of the object being listed
        """

        r_table = Table(response)
        max_ct = data["max"]

        while len(response) == max_ct:
            data["start"] += max_ct
            response = self._post_request(data, "List", object_name)[field]
            r_table.concat(Table(response))

        return r_table

    def get_user_list(self, start_user=0, max_user=999, **kwargs):
        """
        `Args:`
            start_user: int
                The index of first user to return. Starts from 0 (not 1).
            max_user: str
                The index of the max user to return
            **kwargs:
                Any other fields to pass

        `Returns:`
            A Parsons Table of user information for every user from start_user to max_user.
        """
        data = {"start": start_user, "max": max_user, **kwargs}

        return self._get_request_response(data, "List", "User")

    def get_customer_list(self, start_customer=0, max_customer=999, **kwargs):
        """
        `Args:`
            start_customer: int
                The index of first customer to return. Starts from 1 (not 0).
            max_customer: str
                The index of the max customer to return
            **kwargs:
                Any other fields to pass

        `Returns:`
            A Parsons Table of customer information for every user from start_customer
            to max_customer.
        """
        data = {"start": start_customer, "max": max_customer, **kwargs}

        return self._get_request_response(data, "List", "Customer")

    def get_invoice_list(self, start_invoice=0, max_invoice=999, **kwargs):
        """
        `Args:`
            start_invoice: int
                The index of first customer to return. Starts from 1 (not 0).
            max_invoice: str
                The index of the max customer to return
            **kwargs:
                Any other fields to pass

        `Returns:`
            A list of dictionaries of invoice information for every invoice from start_invoice
            to max_invoice.
        """
        data = {"start": start_invoice, "max": max_invoice, **kwargs}

        return self._get_request_response(data, "List", "Invoice")

    def read_customer(self, customer_id):
        """
        `Args:`
            customer_id: str
                The id of the customer to query

        `Returns:`
            A dictionary of the customer's information.
        """
        data = {"id": customer_id}
        return self._get_request_response(data, "Read", "Customer")

    def read_invoice(self, invoice_id):
        """
        `Args:`
            invoice_id: str
                The id of the invoice to query

        `Returns:`
            A dictionary of the invoice information.
        """
        data = {"id": invoice_id}
        return self._get_request_response(data, "Read", "Invoice")

    def check_customer(self, customer1, customer2):
        """
        `Args:`
            customer1: dict
                A dictionary of data on customer1
            customer2: dict
                A dictionary of data on customer2

        `Returns:`
            True if either
                1. customer1 and customer2 have the same id
                OR
                2. customer1 has no id and customer1 customer2 have the same email address
            False otherwise

        """
        if "id" in customer1.keys():
            if customer1["id"] == customer2["id"]:
                return True
        if "id" not in customer1.keys() and customer2["email"]:
            if customer1["email"].lower() == customer2["email"].lower():
                return True
        return False

    def get_or_create_customer(self, customer_name, customer_email, **kwargs):
        """
        `Args:`
            customer_name: str
                The name of the customer
            customer_email: str
                The customer's email
        `Keyword Args:`
            **kwargs:
                Any other fields to store about the customer.

        `Returns:`
            A dictionary of the customer's information including an id.
            If the customer already exists, this function will not
            create a new id and instead use the existing id.
        """
        customer = {"name": customer_name, "email": customer_email, **kwargs}

        # check if customer already exists
        customer_list = self.get_customer_list()
        for existing_customer in customer_list:
            if self.check_customer(customer, existing_customer):
                return existing_customer
        # customer doesn't exist, create
        data = {"obj": customer}
        return self._get_request_response(data, "Create", "Customer")

    def create_invoice(
        self, customer_id, invoice_number, invoice_date, due_date, invoice_line_items, **kwargs
    ):
        """
        `Args:`
            customer_id: str
                The customer's id
            invoice_number: str
                The invoice number. Every invoice must have a distinct
                invoice number.
            invoice_date: str
                The invoice date. This can be the date the invoice was
                generated of any other relevant date.
            due_date: str
                The date on which the invoice is due.
            invoice_line_items: list
                A list of dicts, one for each line item in the invoice.
                The only required field is "quantity".
            **kwargs:
                Any other invoice details to pass.

        `Returns:`
            A dictionary of the invoice's information including an id.
        """
        for invoice_line_item in invoice_line_items:
            if "entity" not in invoice_line_item:
                invoice_line_item["entity"] = "InvoiceLineItem"
        data = {
            "obj": {
                "customerId": customer_id,
                "invoiceNumber": invoice_number,
                "invoiceDate": invoice_date,
                "dueDate": due_date,
                "invoiceLineItems": invoice_line_items,
                **kwargs,
            }
        }
        return self._get_request_response(data, "Create", "Invoice")

    def send_invoice(
        self, invoice_id, from_user_id, to_email_addresses, message_subject, message_body, **kwargs
    ):
        """
        `Args:`
            invoice_id: str
                The id of the invoice to send
            from_user_id: str
                The id of the Bill.com user from whom to send the email
            to_email_addresses:
                The customer's email address
            message_subject:
                The subject of the email to send to the customer
            message_body:
                The body of the email to send to the customer
            **kwargs:
                Any other details for sending the invoice

        `Returns:`
            A dictionary of the sent invoice.
        """
        data = {
            "invoiceId": invoice_id,
            "headers": {
                "fromUserId": from_user_id,
                "toEmailAddresses": to_email_addresses,
                "subject": message_subject,
                **kwargs,
            },
            "content": {"body": message_body},
        }
        return self._get_request_response(data, "Send", "Invoice")
