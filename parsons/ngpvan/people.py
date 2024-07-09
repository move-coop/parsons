from parsons.utilities import json_format
from typing import Union, List, Dict
import logging

logger = logging.getLogger(__name__)


class People(object):
    def __init__(self, van_connection):
        self.connection = van_connection

    def find_person(
        self,
        first_name=None,
        last_name=None,
        date_of_birth=None,
        email=None,
        phone=None,
        phone_type=None,
        street_number=None,
        street_name=None,
        zip=None,
        **kwargs,
    ):
        """
        Find a person record.

        .. note::
            Person find must include the following minimum combinations to conduct
            a search.

              - first_name, last_name, email
              - first_name, last_name, phone
              - first_name, last_name, zip5, date_of_birth
              - first_name, last_name, street_number, street_name, zip5
              - email_address

        `Args:`
            first_name: str
                The person's first name
            last_name: str
                The person's last name
            dob: str
                ISO 8601 formatted date of birth (e.g. ``1981-02-01``)
            email: str
                The person's email address
            phone: str
                Phone number of any type (Work, Cell, Home)
            street_number: str
                Street Number
            street_name: str
                Street Name
            zip: str
                5 digit zip code
            kwargs:
                Any additional keyword arguments will be passed to
                the EveryAction API for matching.
        `Returns:`
            A person dict object
        """

        logger.info(f"Finding {first_name} {last_name}.")

        return self._people_search(
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            email=email,
            phone=phone,
            phone_type=phone_type,
            street_number=street_number,
            street_name=street_name,
            zip=zip,
            **kwargs,
        )

    def find_person_json(self, match_json):
        """
        Find a person record based on json data.

        .. note::
            Person find must include the following minimum combinations to conduct
            a search.

              - first_name, last_name, email
              - first_name, last_name, phone
              - first_name, last_name, zip5, date_of_birth
              - first_name, last_name, street_number, street_name, zip5
              - email_address

        .. note::
            A full list of possible values for the json, and its structure can be found
            `here <https://docs.ngpvan.com/reference/people#peoplefind>`_.

        `Args:`
            match_json: dict
                A dictionary of values to match against.
            fields: The fields to return. Leave as default for all available fields
        `Returns:`
            A person dict object
        """

        logger.info("Finding a match for json details.")

        return self._people_search(match_json=match_json)

    def update_person(
        self,
        id=None,
        id_type="vanid",
        first_name=None,
        last_name=None,
        date_of_birth=None,
        email=None,
        phone=None,
        phone_type=None,
        street_number=None,
        street_name=None,
        zip=None,
    ):
        """
        Update a person record based on a provided ID. All other arguments provided will be
        updated on the record.

        .. warning::
            This method can only be run on MyMembers, EveryAction, MyCampaign databases.

        `Args:`
            id: str
                A valid id
            id_type: str
                A known person identifier type available on this VAN instance.
                Defaults to ``vanid``.
            first_name: str
                The person's first name
            last_name: str
                The person's last name
            dob: str
                ISO 8601 formatted date of birth (e.g. ``1981-02-01``)
            email: str
                The person's email address
            phone: str
                Phone number of any type (Work, Cell, Home)
            phone_type: str
                One of 'H' for home phone, 'W' for work phone, 'C' for cell, 'M' for
                main phone or 'F' for fax line. Defaults to home phone.
            street_number: str
                Street Number
            street_name: str
                Street Name
            zip: str
                5 digit zip code
        `Returns:`
            A person dict
        """

        return self._people_search(
            id=id,
            id_type=id_type,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            email=email,
            phone=phone,
            phone_type=phone_type,
            street_number=street_number,
            street_name=street_name,
            zip=zip,
            create=True,
        )

    def update_person_json(self, id, id_type="vanid", match_json=None):
        """
        Update a person record based on a provided ID within the match_json dict.

        .. note::
            A full list of possible values for the json, and its structure can be found
            `here <https://docs.ngpvan.com/reference/people#peoplevanid>`_.

        `Args:`
            id: str
                A valid id
            id_type: str
                A known person identifier type available on this VAN instance.
                Defaults to ``vanid``.
            match_json: dict
                A dictionary of values to match against and save.
        `Returns:`
            A person dict
        """

        return self._people_search(id=id, id_type=id_type, match_json=match_json, create=True)

    def upsert_person(
        self,
        first_name=None,
        last_name=None,
        date_of_birth=None,
        email: Union[str, List[Dict[str, Union[str, bool]]], None] = None,
        phone=None,
        phone_type=None,
        street_number=None,
        street_name=None,
        zip=None,
        **kwargs,
    ):
        """
        Create or update a person record.

        .. note::
            Person find must include the following minimum combinations.

              - first_name, last_name, email
              - first_name, last_name, phone
              - first_name, last_name, zip5, date_of_birth
              - first_name, last_name, street_number, street_name, zip5
              - email_address

        .. warning::
            This method can only be run on MyMembers, EveryAction, MyCampaign databases.

        `Args:`
            first_name: str
                The person's first name
            last_name: str
                The person's last name
            dob: str
                ISO 8601 formatted date of birth (e.g. ``1981-02-01``)
            email: Union[str, List[Dict[str, Union[str, bool]]], None]
                The person's email address or a list of email dicts.
                e.g. [{'email': 'abcd@gmail.com', 'isSubscribed': False}]
                See https://docs.everyaction.com/reference/people-common-models#email
            phone: str
                Phone number of any type (Work, Cell, Home)
            phone_type: str
                One of 'H' for home phone, 'W' for work phone, 'C' for cell, 'M' for
                main phone or 'F' for fax line. Defaults to home phone.
            street_number: str
                Street Number
            street_name: str
                Street Name
            zip: str
                5 digit zip code
            kwargs:
                Any additional keyword arguments will be passed to
                the EveryAction API for matching.
        `Returns:`
            A person dict
        """

        return self._people_search(
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            email=email,
            phone=phone,
            phone_type=phone_type,
            street_number=street_number,
            street_name=street_name,
            zip=zip,
            create=True,
            **kwargs,
        )

    def upsert_person_json(self, match_json):
        """
        Create or update a person record.

        .. note::
            Person find must include the following minimum combinations.

              - first_name, last_name, email
              - first_name, last_name, phone
              - first_name, last_name, zip5, date_of_birth
              - first_name, last_name, street_number, street_name, zip5
              - email_address

        .. note::
            A full list of possible values for the json, and its structure can be found
            `here <https://docs.ngpvan.com/reference/people#peoplefindorcreate>`_. `vanId` can
            be passed to ensure the correct record is updated.

        .. warning::
            This method can only be run on MyMembers, EveryAction, MyCampaign databases.

        `Args:`
            match_json: dict
                A dictionary of values to match against and save.
        `Returns:`
            A person dict
        """

        return self._people_search(match_json=match_json, create=True)

    def _people_search(
        self,
        id=None,
        id_type=None,
        first_name=None,
        last_name=None,
        date_of_birth=None,
        email: Union[str, List[Dict[str, Union[str, bool]]], None] = None,
        phone=None,
        phone_type="H",
        street_number=None,
        street_name=None,
        zip=None,
        match_json=None,
        create=False,
        **kwargs,
    ):
        # Internal method to hit the people find/create endpoints

        addressLine1 = None
        if street_name and street_number:
            addressLine1 = f"{street_number} {street_name}"

        # Check to see if a match map has been provided
        if not match_json:
            json = {"firstName": first_name, "lastName": last_name}

            # Will fail if empty dicts are provided, hence needed to add if exist
            if email:
                if isinstance(email, str):
                    json["emails"] = [{"email": email}]
                elif isinstance(email, list):
                    json["emails"] = email
                else:
                    raise ValueError(f"Unexpected data type for email argument: {type(email)}")
            if phone:  # To Do: Strip out non-integers from phone
                json["phones"] = [{"phoneNumber": phone, "phoneType": phone_type}]
            if date_of_birth:
                json["dateOfBirth"] = date_of_birth
            if zip or addressLine1:
                json["addresses"] = [{}]
                if zip:
                    json["addresses"][0]["zipOrPostalCode"] = zip
                if addressLine1:
                    json["addresses"][0]["addressLine1"] = addressLine1
        else:
            json = match_json
            if "vanId" in match_json:
                id = match_json["vanId"]

        if kwargs:
            match_json.update(kwargs)

        url = "people/"

        if id:
            if create:
                id_type = "" if id_type in ("vanid", None) else f"{id_type}:"
                url += id_type + str(id)
            else:
                return self.get_person(id, id_type=id_type)

        else:
            url += "find"

            if create:
                url += "OrCreate"
            else:
                # Ensure that the minimum combination of fields were passed
                json_flat = json_format.flatten_json(json)
                self._valid_search(**json_flat)

        return self.connection.post_request(url, json=json)

    def _valid_search(
        self,
        firstName=None,
        lastName=None,
        email=None,
        phoneNumber=None,
        dateOfBirth=None,
        addressLine1=None,
        zipOrPostalCode=None,
        **kwargs,
    ):
        # Internal method to check if a search is valid, kwargs are ignored

        if (
            None in [firstName, lastName, email]
            and None in [firstName, lastName, phoneNumber]
            and None in [firstName, lastName, zipOrPostalCode, dateOfBirth]
            and None in [firstName, lastName, addressLine1, zipOrPostalCode]
            and None in [email]
        ):
            raise ValueError(
                """
                             Person find must include the following minimum
                             combinations to conduct a search.
                                - first_name, last_name, email
                                - first_name, last_name, phone
                                - first_name, last_name, zip, dob
                                - first_name, last_name, street_number, street_name, zip
                                - email
                            """
            )

        return True

    def get_person(
        self,
        id,
        id_type="vanid",
        expand_fields=[
            "contribution_history",
            "addresses",
            "phones",
            "emails",
            "codes",
            "custom_fields",
            "external_ids",
            "preferences",
            "recorded_addresses",
            "reported_demographics",
            "suppressions",
            "cases",
            "custom_properties",
            "districts",
            "election_records",
            "membership_statuses",
            "notes",
            "organization_roles",
            "disclosure_field_values",
        ],
    ):
        """
        Returns a single person record using their VANID or external id.

        `Args:`
            id: str
                A valid id
            id_type: str
                A known person identifier type available on this VAN instance
                such as ``dwid``. Defaults to ``vanid``.
            expand_fields: list
                A list of fields for which to include data. If a field is omitted,
                ``None`` will be returned for that field. Can be ``contribution_history``,
                ``addresses``, ``phones``, ``emails``, ``codes``, ``custom_fields``,
                ``external_ids``, ``preferences``, ``recorded_addresses``,
                ``reported_demographics``, ``suppressions``, ``cases``, ``custom_properties``,
                ``districts``, ``election_records``, ``membership_statuses``, ``notes``,
                ``organization_roles``, ``scores``, ``disclosure_field_values``.
        `Returns:`
            A person dict
        """

        # Change end point based on id type
        url = "people/"

        id_type = "" if id_type in ("vanid", None) else f"{id_type}:"
        url += id_type + str(id)

        # Removing the fields that are not returned in MyVoters
        NOT_IN_MYVOTERS = ["codes", "contribution_history", "organization_roles"]

        if self.connection.db_code == 0:
            expand_fields = [v for v in expand_fields if v not in NOT_IN_MYVOTERS]

        expand_fields = ",".join([json_format.arg_format(f) for f in expand_fields])

        logger.info(f'Getting person with {id_type or "vanid"} of {id} at url {url}')
        return self.connection.get_request(url, params={"$expand": expand_fields})

    def delete_person(self, vanid):
        """
        Suppress the given VANID in databases where contact records can be suppressed.

        `Args:`
            vanid: str
                The person's VAN ID.
        `Returns:`
            Success or error.
        """
        url = f"people/{vanid}"
        r = self.connection.delete_request(url)
        logger.info(f"Van ID {vanid} suppressed.")
        return r

    def apply_canvass_result(
        self,
        id,
        result_code_id,
        id_type="vanid",
        contact_type_id=None,
        input_type_id=None,
        date_canvassed=None,
        phone=None,
    ):
        """
        Apply a canvass result to a person. Use this end point for attempts that do not
        result in a survey response or an activist code (e.g. Not Home).

        `Args:`
            id: str
                A valid person id
            result_code_id : int
                Specifies the result code of the attempt. Valid ids can be found
                by using the :meth:`get_canvass_responses_result_codes`
            id_type: str
                A known person identifier type available on this VAN instance
                such as ``dwid``
            contact_type_id : int
                `Optional`; A valid contact type id
            input_type_id : int
                `Optional`; Defaults to 11 (API Input)
            date_canvassed : str
                `Optional`; ISO 8601 formatted date. Defaults to todays date
            phone: str
                `Optional`; Phone number of any type (Work, Cell, Home)
        `Returns:`
            ``None``
        """

        logger.info(f"Applying result code {result_code_id} to {id_type} {id}.")
        self.apply_response(
            id,
            None,
            id_type=id_type,
            contact_type_id=contact_type_id,
            input_type_id=input_type_id,
            date_canvassed=date_canvassed,
            result_code_id=result_code_id,
            phone=phone,
        )

    def toggle_volunteer_action(
        self,
        id,
        volunteer_activity_id,
        action,
        id_type="vanid",
        result_code_id=None,
        contact_type_id=None,
        input_type_id=None,
        date_canvassed=None,
    ):
        """
        Apply or remove a volunteer action to or from a person.

        `Args:`
            id: str
                A valid person id
            id_type: str
                A known person identifier type available on this VAN instance
                such as ``dwid``
            volunteer_activity_id: int
                A valid volunteer activity id
            action: str
                Either 'apply' or 'remove'
            result_code_id : int
                `Optional`; Specifies the result code of the response. If
                not included,responses must be specified. Conversely, if
                responses are specified, result_code_id must be null. Valid ids
                can be found by using the :meth:`get_canvass_responses_result_codes`
            contact_type_id: int
                `Optional`; A valid contact type id
            input_type_id: int
                `Optional`; Defaults to 11 (API Input)
            date_canvassed: str
                `Optional`; ISO 8601 formatted date. Defaults to todays date

        ** NOT IMPLEMENTED **
        """

        """
        response = {"volunteerActivityId": volunteer_activity_id,
                    "action": self._action_parse(action),
                    "type": "VolunteerActivity"}

        logger.info(f'{action} volunteer activity {volunteer_activity_id} to {id_type} {id}')
        self.apply_response(id, response, id_type, contact_type_id, input_type_id, date_canvassed,
                            result_code_id)
        """

    def apply_response(
        self,
        id,
        response,
        id_type="vanid",
        contact_type_id=None,
        input_type_id=None,
        date_canvassed=None,
        result_code_id=None,
        omit_contact=False,
        phone=None,
        campaignId=None,
    ):
        """
        Apply responses such as survey questions, activist codes, and volunteer actions
        to a person record. This method allows you apply multiple responses (e.g. two survey
        questions) at the same time. It is a low level method that requires that you
        conform to the VAN API `response object
        format <https://docs.ngpvan.com/reference/canvass-responses>`_.

        `Args:`
            id: str
                A valid person id
            response: dict
                A list of dicts with each dict containing a valid action.
            id_type: str
                A known person identifier type available on this VAN instance
                such as ``dwid``
            result_code_id : int
                `Optional`; Specifies the result code of the response. If
                not included,responses must be specified. Conversely, if
                responses are specified, result_code_id must be null. Valid ids
                can be found by using the :meth:`get_canvass_responses_result_codes`
            contact_type_id : int
                `Optional`; A valid contact type id
            input_type_id : int
                `Optional`; Defaults to 11 (API Input)
            date_canvassed : str
                `Optional`; ISO 8601 formatted date. Defaults to todays date
            responses : list or dict
                The responses to apply.
            omit_contact: boolean
                Omit adding contact history to the response. This is particularly
                useful when adding activist codes that are not based on contact
                attempts.
            phone: str
                `Optional`; Phone number of any type (Work, Cell, Home)
            campaignId: int
                `Optional`; a valid Campaign ID.
        `Returns:`
            ``True`` if successful

        .. code-block:: python

            response = [{"activistCodeId": 18917,
                         "action": "Apply",
                         "type": "ActivistCode"},
                        {"surveyQuestionId": 109149,
                         "surveyResponseId": 465468,
                         "type": "SurveyResponse"}
                        ]
            van.apply_response(5222, response)
        """  # noqa: E501,E261

        # Set url based on id_type
        if id_type == "vanid":
            url = f"people/{id}/canvassResponses"
        else:
            url = f"people/{id_type}:{id}/canvassResponses"

        json = {
            "canvassContext": {
                "contactTypeId": contact_type_id,
                "inputTypeId": input_type_id,
                "dateCanvassed": date_canvassed,
                "omitActivistCodeContactHistory": omit_contact,
                "campaignId": campaignId,
            },
            "resultCodeId": result_code_id,
        }

        if (
            contact_type_id == 1  # Phone
            or contact_type_id == 19  # Auto Dial
            or contact_type_id == 37  # SMS Text
            or contact_type_id == 67  # Phone Bank
            or contact_type_id == 68  # Consumer Phone
            or contact_type_id == 72  # Leader Phone
            or contact_type_id == 112  # Personal Phone
            or contact_type_id == 132  # Relational Text
            or contact_type_id == 143  # Distributed Text
            or contact_type_id == 147  # Bulk Text
            or contact_type_id == 149  # Paid SMS
        ):
            if not phone:
                raise Exception("A phone number must be provided if canvassed via phone or SMS")

        if phone:
            json["canvassContext"]["phone"] = {
                "dialingPrefix": "1",
                "phoneNumber": phone,
            }

        if response:
            json["responses"] = response

        if result_code_id is not None and response is not None:
            raise ValueError("Both result_code_id and responses cannot be specified.")

        if isinstance(response, dict):
            json["responses"] = [response]

        if result_code_id is not None and response is not None:
            raise ValueError("Both result_code_id and responses cannot be specified.")

        return self.connection.post_request(url, json=json)

    def create_relationship(self, vanid_1, vanid_2, relationship_id):
        """
        Create a relationship between two individuals

        `Args:`
            vanid_1 : int
                The vanid of the primary individual; aka the node
            vanid_2 : int
                The vanid of the secondary individual; the spoke
            relationship_id : int
                The relationship id indicating the type of relationship
        `Returns:`
            ``None``
        """

        json = {"relationshipId": relationship_id, "vanId": vanid_2}

        self.connection.post_request(f"people/{vanid_1}/relationships", json=json)
        logger.info(f"Relationship {vanid_1} to {vanid_2} created.")

    def apply_person_code(self, id, code_id, id_type="vanid"):
        """
        Apply a code to a person.

        `Args:`
            id: str
                A valid person id.
            code_id: int
                A valid code id.
            id_type: str
                A known person identifier type available on this VAN instance
                such as ``dwid``
        `Returns:`
            ``None``
        """

        # Set url based on id_type
        if id_type == "vanid":
            url = f"people/{id}/codes"
        else:
            url = f"people/{id_type}:{id}/codes"

        json = {"codeId": code_id}

        self.connection.post_request(url, json=json)
        logger.info(f"Code {code_id} applied to person id {id}.")

    def merge_contacts(self, primary_vanid, source_vanid):
        """
        Merges two contacts in EveryAction. The source contact record will be
        deleted as part of the merge and its data will be moved into the primary
        contact record. In cases where fields conflict between the two contacts
        and we can't keep both values, such as if the contacts have different
        first names, the primary contact record's data will be retained. For
        more information see the
        `VAN API documentation here <https://docs.ngpvan.com/reference/peoplevanidmergeinto>`_

        `Args:`
            primary_vanid: str
                The VANID of the primary contact record.
            source_vanid: str
                The VANID of the source contact record.
        `Returns:`
            The VANID of the primary contact record.
        """

        url = f"people/{source_vanid}/mergeInto"
        json = {"vanId": primary_vanid}

        r = self.connection.put_request(url, json=json)
        return r
