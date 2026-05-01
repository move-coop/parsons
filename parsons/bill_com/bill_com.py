import json
from typing import Any, Literal, overload

import requests

from parsons import Table


class BillCom:
    """
    Args:
        user_name: The Bill.com username
        password: The Bill.com password
        org_id: The Bill.com organization id
        dev_key: The Bill.com dev key
        api_url: The Bill.com end point url

    """

    def __init__(
        self, user_name: str, password: str, org_id: str, dev_key: str, api_url: str
    ) -> None:
        self.headers = {"Content-Type": "application/x-www-form-urlencoded"}
        params = {
            "userName": user_name,
            "password": password,
            "orgId": org_id,
            "devKey": dev_key,
        }
        response = requests.post(url=f"{api_url}Login.json", data=params, headers=self.headers)
        self.dev_key = dev_key
        self.api_url = api_url
        self.session_id = response.json()["response_data"]["sessionId"]

    def _get_payload(self, data: dict) -> dict[str, str]:
        """
        Args:
            data:
                A dictionary containing the payload to be sent in the request.
                The dev_key and sessionId should not be
                included as they are dealt with separately.

        Returns:
            The payload to be sent in the request with the ``dev_key`` and ``sessionId`` added.

        """
        return {
            "devKey": self.dev_key,
            "sessionId": self.session_id,
            "data": json.dumps(data),
        }

    def _post_request(
        self,
        data: dict,
        action: Literal["List", "Read", "Create", "Send"],
        object_name: Literal["User", "Customer", "Invoice"],
    ) -> dict[str, Any]:
        """
        Args:
            data:
                A dictionary containing the payload to be sent in the request.
                The dev_key and sessionId should not be included
                as they are dealt with separately.
            action:
                The action to be taken on the given object.
                Possible values are ``List``, ``Read``, ``Create``, and ``Send``.
            object_name:
                The id of the object.
                Possible values are ``User``, ``Customer``, and ``Invoice``.

        Returns:
            The JSON response from the post request.

        """
        if action == "Read":
            url = f"{self.api_url}Crud/{action}/{object_name}.json"
        elif action == "Create":
            data["obj"]["entity"] = object_name
            url = f"{self.api_url}Crud/{action}/{object_name}.json"
        elif action == "Send":
            url = f"{self.api_url}{action}{object_name}.json"
        else:
            url = f"{self.api_url}{action}/{object_name}.json"
        payload = self._get_payload(data)
        response = requests.post(url=url, data=payload, headers=self.headers)
        return response.json()

    @overload
    def _get_request_response(
        self,
        data: dict[str, Any],
        action: Literal["List"],
        object_name: Literal["User", "Customer", "Invoice"],
        field: str = ...,
    ) -> Table: ...

    @overload
    def _get_request_response(
        self,
        data: dict[str, Any],
        action: Literal["Read", "Create", "Send"],
        object_name: Literal["User", "Customer", "Invoice"],
        field: str = ...,
    ) -> dict[str, Any]: ...

    def _get_request_response(
        self,
        data: dict[str, Any],
        action: Literal["List", "Read", "Create", "Send"],
        object_name: Literal["User", "Customer", "Invoice"],
        field: str = "response_data",
    ) -> dict[str, Any] | Table:
        """
        Args:
            data:
                A dictionary containing the payload to be sent in the request.
                The dev_key and sessionId should not be included as they are dealt with separately.
            action:
                The action to be taken on the given object.
                Possible values are ``List``, ``Read``, ``Create``, and ``Send``.
            object_name:
                The id of the object.
                Possible values are ``User``, ``Customer``, and ``Invoice``.
            field:
                The JSON field where the response data is stored.
                Defaults to ``response_data``.

        Returns:
            A dictionary containing the choosen field from the JSON response from the post request.

        """
        r = self._post_request(data, action, object_name)[field]

        if action == "List":
            return self._paginate_list(r, data, object_name)

        return r

    def _paginate_list(
        self,
        response: list[dict],
        data: dict[str, Any],
        object_name: Literal["User", "Customer", "Invoice"],
        field: str = "response_data",
    ) -> Table:
        """
        Internal method to paginate through and concatenate results of lists larger than max.

        Args:
            response: Data from an initial list call
            data: Start, max, and kwargs from initial list call
            object_name: Name of the object being listed

        """
        r_table = Table(response)
        max_ct = data["max"]

        while len(response) == max_ct:
            data["start"] += max_ct
            response = self._post_request(data, "List", object_name)[field]
            r_table.concat(Table(response))

        return r_table

    def get_user_list(self, start_user: int = 0, max_user: int = 999, **kwargs) -> Table:
        """
        Args:
            start_user:
                The index of first user to return.
                Starts from 0 (not 1).
            max_user: The index of the max user to return
            `**kwargs`: Any other fields to pass

        Returns:
            User information for every user from `start_user` to `max_user`

        """
        data = {"start": start_user, "max": max_user, **kwargs}

        return self._get_request_response(data, "List", "User")

    def get_customer_list(
        self, start_customer: int = 0, max_customer: int = 999, **kwargs
    ) -> Table:
        """
        Args:
            start_customer:
                The index of first customer to return.
                Starts from 1 (not 0).
            max_customer:  The index of the max customer to return
            `**kwargs`: Any other fields to pass

        Returns:
            Customer information for every user from `start_customer` to `max_customer`

        """
        data = {"start": start_customer, "max": max_customer, **kwargs}

        return self._get_request_response(data, "List", "Customer")

    def get_invoice_list(self, start_invoice: int = 0, max_invoice: int = 999, **kwargs) -> Table:
        """
        Args:
            start_invoice:
                The index of first customer to return.
                Starts from 1 (not 0).
            max_invoice: The index of the max customer to return
            `**kwargs`: Any other fields to pass

        Returns:
            Invoice information for every invoice from `start_invoice` to `max_invoice`.

        """
        data = {"start": start_invoice, "max": max_invoice, **kwargs}

        return self._get_request_response(data, "List", "Invoice")

    def read_customer(self, customer_id: str) -> dict[str, Any]:
        """
        Args:
            customer_id: str
                The id of the customer to query

        Returns:
            The customer's information.

        """
        data = {"id": customer_id}
        return self._get_request_response(data, "Read", "Customer")

    def read_invoice(self, invoice_id: str) -> dict[str, Any]:
        """
        Args:
            invoice_id: The id of the invoice to query

        Returns:
            The invoice information.

        """
        data = {"id": invoice_id}
        return self._get_request_response(data, "Read", "Invoice")

    def check_customer(self, customer1: dict[str, Any], customer2: dict[str, Any]) -> bool:
        """
        Args:
            customer1: A dictionary of data on customer1
            customer2: A dictionary of data on customer2

        Returns:
            ``True`` if either

            1. customer1 and customer2 have the same id
            OR
            2. customer1 has no id and customer1 customer2 have the same email address

            ``False`` otherwise

        """
        if "id" in customer1 and customer1["id"] == customer2["id"]:
            return True
        return bool(
            ("id" not in customer1 and customer2["email"])
            and customer1["email"].lower() == customer2["email"].lower()
        )

    def get_or_create_customer(
        self, customer_name: str, customer_email: str, **kwargs
    ) -> dict[str, Any] | Table:
        """
        Args:
            customer_name: The name of the customer
            customer_email: The customer's email

        Keyword Args:
            `**kwargs`: Any other fields to store about the customer.

        Returns:
            The customer's information including an id.
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
        self,
        customer_id: str,
        invoice_number: str,
        invoice_date: str,
        due_date: str,
        invoice_line_items: list[dict],
        **kwargs,
    ) -> dict[str, Any]:
        """
        Args:
            customer_id: The customer's id
            invoice_number:
                The invoice number.
                Every invoice must have a distinct invoice number.
            invoice_date: str
                The invoice date.
                This can be the date the invoice was generated of any other relevant date.
            due_date: The date on which the invoice is due.
            invoice_line_items:
                A list of dicts, one for each line item in the invoice.
                The only required field is "quantity".
            `**kwargs`: Any other invoice details to pass.

        Returns:
            The invoice's information including an id.

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
        self,
        invoice_id: str,
        from_user_id: str,
        to_email_addresses: str,
        message_subject: str,
        message_body: str,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Args:
            invoice_id: The id of the invoice to send
            from_user_id: The id of the Bill.com user from whom to send the email
            to_email_addresses: The customer's email address
            message_subject: The subject of the email to send to the customer
            message_body: The body of the email to send to the customer
            `**kwargs`: Any other details for sending the invoice

        Returns:
            The sent invoice.

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
