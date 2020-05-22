import json
from parsons import Table
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector
import logging

logger = logging.getLogger(__name__)


class ActionNetwork(object):
    """
    `Args:`
        api_token: str
            The OSDI API token
        api_url:
            The end point url
    """
    def __init__(self, api_token=None, api_url=None):
        self.api_token = check_env.check('AN_API_TOKEN', api_token)
        self.headers = {
            "Content-Type": "application/json",
            "OSDI-API-Token": self.api_token
        }
        self.api_url = check_env.check('AN_API_URL', api_url)
        self.api = APIConnector(self.api_url, headers=self.headers)

    def _get_page(self, object_name, page, per_page=25):
        # returns data from one page of results
        if per_page > 25:
            per_page = 25
            logger.info("Action Network's API will not return more than 25 entries per page. \
            Changing per_page parameter to 25.")
        page_url = f"{self.api_url}/{object_name}?page={page}&per_page={per_page}"
        return self.api.get_request(url=page_url)

    def _get_entry_list(self, object_name, limit=None, per_page=25):
        # returns a list of entries for a given object, such as people, tags, or actions
        count = 0
        page = 1
        return_list = []
        while True:
            response = self._get_page(object_name, page, per_page)
            page = page + 1
            response_list = response['_embedded'][f"osdi:{object_name}"]
            if not response_list:
                return Table(return_list)
            return_list.extend(response_list)
            count = count + len(response_list)
            if limit:
                if count >= limit:
                    return Table(return_list[0:limit])

    def get_people(self, limit=None, per_page=25, page=None):
        """
        `Args:`
            limit:
                The number of entries to return. When None, returns all entries.
            per_page
                The number of entries per page to return. 25 maximum.
            page
                Which page of results to return
        `Returns:`
            A list of JSONs of people stored in Action Network.
        """
        if page:
            self._get_page("people", page, per_page)
        return self._get_entry_list("people", limit, per_page)

    def get_person(self, person_id):
        """
        `Args:`
            person_id:
                Id of the person.
        `Returns:`
            A  JSON of the entry. If the entry doesn't exist, Action Network returns
            ``{'error': 'Couldn't find person with id = <id>'}``.
        """
        return self.api.get_request(url=f"{self.api_url}/people/{person_id}")

    def add_person(self, email_address, given_name=None, family_name=None, tags=[],
                   languages_spoken=[], postal_addresses=[],
                   **kwargs):
        """
        `Args:`
            email_address:
                Can be any of the following
                    - a string with the person's email
                    - a dictionary with the following fields
                        - email_address (REQUIRED)
                        - primary (OPTIONAL): Boolean indicating the user's primary email address
                        - status (OPTIONAL): can taken on any of these values
                            - "subscribed"
                            - "unsubscribed"
                            - "bouncing"
                            - "previous bounce"
                            - "spam complaint"
                            - "previous spam complaint"
            given_name:
                The person's given name
            family_name:
                The person's family name
            tags:
                Any tags to be applied to the person
            languages_spoken:
                Optional field. A list of strings of the languages spoken by the person
            postal_addresses:
                Optional field. A list of dictionaries.
                For details, see Action Network's documentation:
                https://actionnetwork.org/docs/v2/people#put
            **kwargs:
                Any additional fields to store about the person. Action Network allows
                any custom field.
        Adds a person to Action Network
        """
        email_addresses_field = None
        if type(email_address) == str:
            email_addresses_field = [{"address": email_address}]
        elif type(email_address == list):
            if type(email_address[0]) == str:
                email_addresses_field = [{"address": email} for email in email_address]
                email_addresses_field[0]['primary'] = True
            if type(email_address[0]) == dict:
                email_addresses_field = email_address
        if not email_addresses_field:
            raise("email_address must be a string, list of strings, or list of dictionaries")
        data = {
            "person": {
                "email_addresses": email_addresses_field,
                "given_name": given_name,
                "family_name": family_name,
                "languages_spoken": languages_spoken,
                "postal_addresses": postal_addresses,
                "custom_fields": {**kwargs}
              },
            "add_tags": tags
        }
        response = self.api.post_request(url=f"{self.api_url}/people", data=json.dumps(data))
        identifiers = response['identifiers']
        person_id = [entry_id.split(':')[1]
                     for entry_id in identifiers if 'action_network:' in entry_id][0]
        logger.info(f"Entry {person_id} successfully added to people.")
        return response

    def update_person(self, entry_id, **kwargs):
        """
        `Args:`
            entry_id:
                The person's Action Network id
            **kwargs:
                Fields to be updated. The possible fields are
                    email_address:
                        Can be any of the following
                            - a string with the person's email
                            - a dictionary with the following fields
                                - email_address (REQUIRED)
                                    - primary (OPTIONAL): Boolean indicating the user's
                                    primary email address
                                - status (OPTIONAL): can taken on any of these values
                                    - "subscribed"
                                    - "unsubscribed"
                                    - "bouncing"
                                    - "previous bounce"
                                    - "spam complaint"
                                    - "previous spam complaint"
                    given_name:
                        The person's given name
                    family_name:
                        The person's family name
                    tags:
                        Any tags to be applied to the person
                    languages_spoken:
                        Optional field. A list of strings of the languages spoken by the person
                    postal_addresses:
                        Optional field. A list of dictionaries.
                        For details, see Action Network's documentation:
                        https://actionnetwork.org/docs/v2/people#put
                    custom_fields:
                        A dictionary of any other fields to store about the person.
        Updates a person's data in Action Network
        """
        data = {**kwargs}
        response = self.api.put_request(url=f"{self.api_url}/people/{entry_id}",
                                        json=json.dumps(data), success_codes=[204, 201, 200])
        logger.info(f"Person {entry_id} successfully updated")
        return response

    def get_tags(self, limit=None, per_page=25, page=None):
        """
        `Args:`
            limit:
                The number of entries to return. When None, returns all entries.
            per_page
                The number of entries per page to return. 25 maximum.
            page
                Which page of results to return
        `Returns:`
            A list of JSONs of tags in Action Network.
        """
        if page:
            self.get_page("tags", page, per_page)
        return self._get_entry_list("tags", limit, per_page)

    def get_tag(self, tag_id):
        """
        `Args:`
            tag_id:
                Id of the tag.
        `Returns:`
            A  JSON of the entry. If the entry doesn't exist, Action Network returns
            "{'error': 'Couldn't find tag with id = <id>'}"
        """
        return self.api.get_request(url=f"{self.api_url}/tags/{tag_id}")

    def add_tag(self, name):
        """
        `Args:`
            name:
                The tag's name. This is the ONLY editable field
        Adds a tag to Action Network. Once created, tags CANNOT be edited or deleted.
        """
        data = {
            "name": name
        }
        response = self.api.post_request(url=f"{self.api_url}/tags", data=json.dumps(data))
        identifiers = response['identifiers']
        person_id = [entry_id.split(':')[1]
                     for entry_id in identifiers if 'action_network:' in entry_id][0]
        logger.info(f"Tag {person_id} successfully added to tags.")
        return response
