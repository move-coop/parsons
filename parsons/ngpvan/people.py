from parsons.utilities import json_format
from parsons.utilities.converted_dict import converted_dict
import logging

logger = logging.getLogger(__name__)


class People(object):

    def __init__(self, van_connection):

        self.connection = van_connection

    def find_person(self, id=None, id_type=None, expand_fields=None, first_name=None,
                    last_name=None, date_of_birth=None, email=None, phone_number=None,
                    address_line1=None, zip=None, match_map=None):
        """
        Find a person record.

        .. note::
            Person find must include VAN ID or one the following minimum combinations
            to conduct a search.

            - first_name, last_name, email
            - first_name, last_name, phone_number
            - first_name, last_name, zip5, date_of_birth
            - first_name, last_name, street_number, street_name, zip5
            - email_address

        .. note::
            The arguments that can be passed are a selection of the possible values that
            can be used in a search. A full list of possible values can be found
            `here <https://developers.ngpvan.com/van-api#match-candidates>`_. To use these
            values, pass in a dictionary using the match_map argument. To expand objects
            such as phones, emails, etc. make sure to include a comma-separated list in
            match_map with the key as `'$expand'`  - for more details, see
            - see `VAN docs <https://developers.ngpvan.com/van-api#people-get-people--vanid>`_.

        `Args:`
            id: int or str
                Any of the record's unique identifiers (e.g. VAN ID) if already known
            id_type: str
                If `id` is provided, this is the person ID type (defaults to 'vanid')
            expand_fields: list
                List of nested fields to expand for full data (e.g. emails, addresses, etc.)
                Only relevant if `id` is provided, defaults to all expandable fields
                - see `VAN docs <https://developers.ngpvan.com/van-api#people-get-people--vanid>`_.
            first_name: str
                The person's first name
            last_name: str
                The person's last name
            dob: str
                ISO 8601 formatted date of birth (e.g. ``1981-02-01``)
            email: str
                The person's email address
            phone_number: str
                Phone number of any type (Work, Cell, Home)
            address_line1: str
                Must contain Street Number and Street Name
            zip: str
                5 digit zip code
            match_map: dict
                A dictionary of values to match against. Will override all
                other arguments if provided.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        logger.info(f'Finding {first_name} {last_name}.')

        return self._people_search(id, id_type, expand_fields, first_name, last_name, date_of_birth,
                                   email, phone_number, address_line1, zip, match_map)

    def upsert_person(self, id=None, id_type=None, first_name=None, last_name=None,
                      date_of_birth=None, email=None, phone_number=None, address_line1=None,
                      zip=None, match_map=None):
        """
        Create or update a person record.

        .. note::
            Person find must include VAN ID or one of the following minimum combinations.

            - first_name, last_name, email
            - first_name, last_name, phone_number
            - first_name, last_name, zip5, date_of_birth
            - first_name, last_name, street_number, street_name, zip5
            - email_address

        .. note::
            The arguments that can be passed are a selection of the possible values that
            can be used in a search. A full list of possible values can be found
            `here <https://developers.ngpvan.com/van-api#match-candidates>`_. To use these
            values, pass in a dictionary using the match_map argument.

        .. warning::
            This method can only be run on MyMembers, EveryAction, MyCampaign databases.

        `Args:`
            id: int or str
                Any of the record's unique identifiers (e.g. VAN ID) if already known
            id_type: str
                If `id` is provided, this is the person ID type (defaults to 'vanid')
            first_name: str
                The person's first name
            last_name: str
                The person's last name
            dob: str
                ISO 8601 formatted date of birth (e.g. ``1981-02-01``)
            email: str
                The person's email address
            phone_number: str
                Phone number of any type (Work, Cell, Home)
            address_line1: str
                Must contain Street Number and Street Name
            zip: str
                5 digit zip code
            match_map: dict
                A dictionary of values to match against. Will override all
                other arguments if provided.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        return self._people_search(id, id_type, None, first_name, last_name, date_of_birth, email,
                                   phone_number, address_line1, zip, match_map, create=True)

    def _people_search(self, id=None, id_type=None, expand_fields=None, first_name=None,
                       last_name=None, date_of_birth=None, email=None, phone_number=None,
                       address_line1=None, zip_or_postal_code=None, match_map=None, create=False):
        # Internal method to hit the people find/create endpoints

        # Check to see if a match map has been provided
        if match_map is None:
            match_map = {}
        match_map.update({"first_name": first_name, "last_name": last_name})

        # Will fail if empty dicts are provided, hence needed to add if exist
        if email is not None:
            match_map['emails'] = [{'email': email}]
        if phone_number is not None:  # To Do: Strip out non-integers from phone
            match_map['phones'] = [{'phone_number': phone_number}]
        if date_of_birth is not None:
            match_map['date_of_birth'] = date_of_birth
        if zip_or_postal_code is not None or address_line1 is not None:
            match_map['addresses'] = []
            if zip_or_postal_code is not None:
                match_map['addresses'][0]['address_line1'] = address_line1
            if address_line1 is not None:
                match_map['addresses'][0]['zip_or_postal_code'] = zip_or_postal_code

        json = converted_dict(match_map, json_format.arg_format).result
        # Check if VANID actually supplied in match_map
        if 'vanid' in [k.lower() for k in match_map]:
            id = {k.lower(): v for k, v in match_map.items()}['vanid']

        if id is None:

            # Ensure that the minimum combination of fields were passed
            self._valid_search(json)

            # Determine correct url
            url = self.connection.uri + 'people/find'
            if create:
                url = url + 'orCreate'

            req_type = 'POST'

        # An id was provided
        else:

            # Determine whether the id type needs to be in the url
            url_id = "" if id_type is None else f"{id_type}:"

            url = self.connection.uri + 'people/' + url_id + str(id)
            req_type = 'GET'
            params = None
            if create:
                req_type = 'POST'
            else:
                # If not creating a new record the expand fields need to be added as param
                if isinstance(expand_fields, str):
                    expand_fields = [expand_fields]
                elif expand_fields is None:
                    expand_fields = ['contributionHistory', 'addresses', 'phones', 'emails',
                                     'codes', 'customFields', 'externalIds', 'preferences',
                                     'recordedAddresses', 'reportedDemographics', 'suppressions',
                                     'cases', 'customProperties', 'districts', 'electionRecords',
                                     'membershipStatuses', 'notes', 'organizationRoles',
                                     'disclosureFieldValues']
                params = {"$expand": ','.join(expand_fields)}

        if req_type == 'POST':
            return self.connection.request(url, req_type="POST", post_data=json)
        else:
            return self.connection.request(url, req_type="GET", args=params)

    def _valid_search(self, json):
        # Internal method to check if a search is valid

        # Flatten the JSON so that we get the bottom-level keys for comparison
        keys = set()
        for k, v in json.items():
            if isinstance(v, list):
                for x in v:
                    for i in x:
                        keys.add(i)
            elif v is not None:
                keys.add(k)

        if (len({'firstName', 'lastName', 'email'} - keys) > 0 and
            len({'firstName', 'lastName', 'phoneNumber'} - keys) > 0 and
            len({'firstName', 'lastName', 'zipOrPostalCode', 'dateOfBirth'} - keys) > 0 and
            len({'firstName', 'lastName', 'addressLine1', 'zipOrPostalCode'} - keys) > 0 and
                'email' not in keys):

            raise ValueError("""
                             Person find must include the following minimum
                             combinations to conduct a search.
                                - first_name, last_name, email
                                - first_name, last_name, phone
                                - first_name, last_name, zip, dob
                                - first_name, last_name, street_number, street_name, zip
                                - email
                            """)

        return True

    def get_person(self, id, id_type='vanid',
                   fields=['emails', 'phones', 'custom_fields', 'external_ids', 'addresses',
                           'recorded_addresses', 'preferences', 'suppressions',
                           'reported_demographics', 'disclosure_field_values']):
        """
        Returns a single person record using their VANID or external id.

        `Args:`
            id: str
                A valid id
            id_type: str
                A known person identifier type available on this VAN instance
                such as ``dwid``
            fields: The fields to return. Leave as default for all available fields
        `Returns:`
            A person dict
        """

        url = self.connection.uri + 'people/find'

        # Change end point based on id type
        if id_type == 'vanid':
            url = self.connection.uri + f'people/{id}'
        else:
            url = self.connection.uri + f'people/{id_type}:{id}'

        fields = ','.join([json_format.arg_format(f) for f in fields])

        logger.info(f'Getting person with {id_type} of {id}')
        return self.connection.request(url, args={'$expand': fields}, raw=True).json()

    def apply_canvass_result(self, id, result_code_id, id_type='vanid', contact_type_id=None,
                             input_type_id=None, date_canvassed=None):
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
        """

        logger.info(f'Applying result code {result_code_id} to {id_type} {id}.')
        self.apply_response(id, None, id_type=id_type, contact_type_id=contact_type_id,
                            input_type_id=input_type_id, date_canvassed=date_canvassed,
                            result_code_id=result_code_id)

        return True

    def apply_survey_response(self, id, survey_question_id, survey_response_id,
                              id_type='vanid', result_code_id=None, contact_type_id=None,
                              input_type_id=None, date_canvassed=None):
        """
        Apply a single survey response to a person.

        `Args:`
            id: str
                A valid person id
            survey_question_id: int
                A valid survey question id
            survey_response_id: int
                A valid survey response id
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
        """

        response = {"surveyQuestionId": survey_question_id,
                    "surveyResponseId": survey_response_id,
                    "type": "surveyResponse"}

        logger.info(f'Applying survey question {survey_question_id} to {id_type} {id}')
        self.apply_response(id, response, id_type, result_code_id=result_code_id,
                            contact_type_id=contact_type_id, input_type_id=input_type_id,
                            date_canvassed=date_canvassed)

        return True

    def toggle_activist_code(self, id, activist_code_id, action, id_type='vanid',
                             result_code_id=None, contact_type_id=None, input_type_id=None,
                             date_canvassed=None):
        """
        Apply or remove an activist code to or from a person.

        `Args:`
            id: str
                A valid person id
            activist_code_id: int
                A valid activist code id
            action: str
                Either 'apply' or 'remove'
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
        """

        response = {"activistCodeId": activist_code_id,
                    "action": self._action_parse(action),
                    "type": "activistCode"}

        logger.info(f'{id_type.upper()} {id} {action.capitalize()} ' +
                    f'activist code {activist_code_id}')
        self.apply_response(id, response, id_type, result_code_id=result_code_id,
                            contact_type_id=contact_type_id, input_type_id=input_type_id,
                            date_canvassed=date_canvassed)

        return True

    def toggle_volunteer_action(self, id, volunteer_activity_id, action, id_type='vanid',
                                result_code_id=None, contact_type_id=None, input_type_id=None,
                                date_canvassed=None):
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

    def _action_parse(self, action):
        # Internal method to parse and validate actions

        action = action.capitalize()

        if action not in ('Apply', 'Remove'):

            raise ValueError("Action must be either 'Apply' or 'Remove'")

        return action

    def apply_response(self, id, response, id_type='vanid', contact_type_id=None,
                       input_type_id=None, date_canvassed=None, result_code_id=None):
        """
        Apply responses such as survey questions, activist codes, and volunteer actions
        to a person record. This method allows you apply multiple responses (e.g. two survey
        questions) at the same time. It is a low level method that requires that you
        conform to the VAN API `response object format <https://developers.ngpvan.com/van-api#people-post-people--vanid--canvassresponses>`_.

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
        `Returns:`
            ``True`` if successful

        .. code-block:: python

            response = [{"activistCodeId": 18917,
                         "action": "Apply",
                         "type": "ActivistCode"},
                        {"surveyQuestionId": 109149,
                         "surveyResponseId": 465468,
                         "action": "SurveyResponse"}
                        ]
            van.apply_response(5222, response)
        """ # noqa: E501,E261

        # Set url based on id_type
        if id_type == 'vanid':
            url = self.connection.uri + f"people/{id}/canvassResponses"
        else:
            url = self.connection.uri + f"people/{id_type}:{id}/canvassResponses"

        json = {"canvassContext": {
            "contactTypeId": contact_type_id,
            "inputTypeId": input_type_id,
            "dateCanvassed": date_canvassed
        },
            "resultCodeId": result_code_id
        }

        if response:
            json['responses'] = response

        if result_code_id is not None and response is not None:
            raise ValueError("Both result_code_id and responses cannot be specified.")

        if isinstance(response, dict):
            json["responses"] = [response]

        if result_code_id is not None and response is not None:
            raise ValueError(
                "Both result_code_id and responses cannot be specified.")

        r = self.connection.request(url, req_type="POST", post_data=json, raw=True)

        # Will probably want to generalize this at some point in the future
        # for other methods, but leaving this here for now.
        if r[0] == 204:
            logger.info(f'{id_type.upper()} {id} updated.')
        else:
            logger.info(f"{r[1]['errors'][0]['code']}: {r[1]['errors'][0]['text']}")
            raise ValueError(f"{r[1]['errors'][0]['text']}")

        return True

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
            Tuple of ``(204, No Content)`` if successful, ``(404, Not Found)``.
        """

        url = self.connection.uri + f"people/{vanid_1}/relationships"

        json = {'relationshipId': relationship_id,
                'vanId': vanid_2}

        return self.connection.request(url, req_type="POST", post_data=json, raw=True)
