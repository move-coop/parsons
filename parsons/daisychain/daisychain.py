from typing import Optional, Union

from parsons.utilities.api_connector import APIConnector


class Daisychain:
    def __init__(self, api_token: str):
        self.connection = APIConnector(
            "https://go.daisychain.app/api/v1/", headers={"X-API-Token": api_token}
        )

    def request(
        self,
        endpoint: str,
        method: str,
        data_key: str,
        json: Optional[Union[list, dict]] = None,
    ) -> list[dict]:
        """Get request with pagination."""
        results = []
        response = self.connection.request(endpoint, method, json=json)
        self.connection.validate_response(response)
        response_data = response.json()
        results.extend(response_data.get(data_key, []))
        while response_data.get("meta", {}).get("next_page"):
            response = self.connection.request(
                url=endpoint,
                req_type=method,
                json=json,
                params={"page": response["meta"]["next_page"]},
            )
            self.connection.validate_response(response)
            response_data = response.json()
            results.extend(response_data.get(data_key, []))
        return results

    def find_person(
        self, email_address: Optional[str] = None, phone_number: Optional[str] = None
    ) -> list[dict]:
        """
        Find a person by email address and/or phone number.

        If multiple parameters are provided, they will be
        combined with AND logic. All parameters are optional,
        but at least one must be provided.

        Parameters:
          email_address (string):
            Email address of the person to match. This is a case
            insensitive match. In Daisychain it is possible for
            multiple people records to have the same email address.
          phone_number (string):
            Phone number of the person to match. In Daisychain
            it is possible for multiple people records to have the
            same phone number. We will do our best to parse any
            string provided, but E.164 format is preferred

        Returns:
          a list of person dictionaries
        """
        assert email_address or phone_number, (
            "At least one of email address or phone number must be provided."
        )
        payload: dict[str, dict[str, str]] = {"person": {}}
        if email_address:
            payload["person"]["email"] = email_address
        if phone_number:
            payload["person"]["phone_number"] = phone_number

        result = self.request("people/match", "post", data_key="people", json=payload)

        return result

    def post_action(
        self,
        email_address: Optional[str] = None,
        phone_number: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        addresses: Optional[list[dict]] = None,
        email_opt_in: bool = False,
        sms_opt_in: bool = False,
        action_data: Optional[dict] = None,
    ) -> str:
        """Record an action on a person in Daisychain.

        Actions are events that are associated with People. They're
        things that people have done or things that have happened
        to them.

            Actions of this kind have no defined schema
            and can contain any data that you want, represented as
            json. The actions will appear in the timeline view of the
            person they are associated with and can be used to trigger
            automations.

            If used as the trigger for an automation it is possible to
            write a jmespath expression in the Daisychain automation
            builder to match against the data in the action. This can
            be used to filter automation executions based on the data
            you or another system provides. For example, you could
            create an action with a action_data field of {"type":
            "donation"} and then use the jmespath expression
            action.type == 'donation' to match against it while
            authoring an automation. This feature can be used to
            create powerful automations that can be triggered by any
            external system that can make an API call.

        Person Creation and Match

            The action creation endpoint is designed to allow other
            systems to create actions for people in Daisychain without
            knowing in advance whether or not that person already
            exists.

            It will create a person if one does not exist with the
            provided email or phone number. If a person does exist
            with the provided email or phone number, the action will
            be associated with that person. Daisychain matches on
            email and phone number in that order of priority. If
            different people exist with the provided email and phone
            number, the action will be associated with the person with
            the matching email.

        Parameters:

        Returns:
          person id (string)

        """
        assert email_address or phone_number, (
            "At least one of email address or phone number must be provided."
        )
        if not action_data:
            action_data = {}
        payload = {
            "person": {
                "first_name": first_name,
                "last_name": last_name,
                "addresses": addresses,
                "phones": [{"value": phone_number}],
                "emails": [{"value": email_address}],
                "email_opt_in": email_opt_in,
                "phone_opt_in": sms_opt_in,
            },
            "action_data": action_data,
        }
        response = self.connection.post_request("actions", json=payload)
        person_id = response["person"]["id"]
        return person_id
