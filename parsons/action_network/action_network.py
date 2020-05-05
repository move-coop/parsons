import json
from time import time
from parsons import Table
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
    def __init__(self, api_token, api_url="https://actionnetwork.org/api/v2/"):
        self.headers = {
            "Content-Type": "application/json",
            "OSDI-API-Token": api_token
        }
        self.api_url = api_url
        self.api = APIConnector(self.api_url, headers=self.headers)

    def _get_entry_list(self, object_name, limit=10, timeout=60):
        # returns a list of entries for a given object, such as people, tags, or actions
        count = 0
        page = 1
        t0 = time()
        return_list = []
        while True:
            if page == 1:
                response = self.api.get_request(url=f"{self.api_url}/{object_name}")
            else:
                response = self.api.get_request(url=f"{self.api_url}/{object_name}?page={page}")
            page = page + 1
            response_list = response['_embedded'][f"osdi:{object_name}"]
            if not response_list:
                return Table(return_list)
            return_list.extend(response_list)
            count = count + len(response_list)
            if limit:
                if count >= limit:
                    return Table(return_list[0:limit])
            if time() - t0 > timeout:
                logger.info("Request timed out. Returning results so far.")
                return Table(return_list)

    def _get_entry(self, object_name, object_id):
        # returns a specific entry by object name and id
        return self.api.get_request(url=f"{self.api_url}/{object_name}/{object_id}")

    def _add_entry(self, object_name, data, silent=False):
        # adds an entry to action network
        response = self.api.post_request(url=f"{self.api_url}/{object_name}", data=json.dumps(data))
        if not silent:
            identifiers = response['identifiers']
            entry_id = [entry_id.split(':')[1]
                        for entry_id in identifiers if 'action_network:' in entry_id][0]
            logger.info(f"Entry {entry_id} successfully added to {object_name}")

    def _update_entry(self, object_name, entry_id, data, silent=False):
        # updates fields for a given entry
        # only the fields to be updated need to be included
        response = self.api.put_request(url=f"{self.api_url}/{object_name}/{entry_id}",
                                        json=json.dumps(data), success_codes=[204, 201, 200])
        if not silent:
            logger.info(f"{object_name.capitalize()} entry {entry_id} successfully updated")
        return response

    def get_people_list(self, limit=10, timeout=60):
        """
        `Args:`
            limit:
                The number of entries to return. When None, returns all entries.
            timeout:
                Seconds before request is forced to timeout. Implemented to ensur no infinite loops.
        `Returns:`
            A list of JSONs of people stored in Action Network.
        """
        return self._get_entry_list("people", limit, timeout)

    def get_person(self, object_id):
        """
        `Args:`
            object_id:
                Id of the person.
        `Returns:`
            A  JSON of the entry. If the entry doesn't exist, Action Network returns
            "{'error': 'Couldn't find <object_name> with id = <id>'}"
        """
        return self._get_entry("people", object_id)

    def add_person(self, email_address, given_name=None, family_name=None, tags=[],
                   languages_spoken=[], postal_addresses=[],
                   silent=False, **kwargs):
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
            silent:
                If true, prints to the person's Action Network id when added successfully
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
        self._add_entry("people", data, silent)

    def update_person(self, entry_id, silent=False, **kwargs):
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
                    silent:
                        If true, prints to the person's Action Network id when added successfully
                    custom_fields:
                        A dictionary of any other fields to store about the person.
        Updates a person's data in Action Network
        """
        data = {**kwargs}
        return self._update_entry("people", entry_id, data, silent)

    def get_tag_list(self, limit=10, timeout=60):
        """
        `Args:`
            limit:
                The number of entries to return. When None, returns all entries.
            timeout:
                Seconds before request is forced to timeout. Implemented to ensur no infinite loops.
        `Returns:`
            A list of JSONs of tags in Action Network.
        """
        return self._get_entry_list("tags", limit, timeout)

    def get_tag(self, object_id):
        """
        `Args:`
            object_id:
                Id of the tag.
        `Returns:`
            A  JSON of the entry. If the entry doesn't exist, Action Network returns
            "{'error': 'Couldn't find <object_name> with id = <id>'}"
        """
        return self._get_entry("tags", object_id)

    def add_tag(self, name, silent=False):
        """
        `Args:`
            name:
                The tag's name. This is the ONLY editable field
            silent:
                If true, prints to the person's Action Network id when added successfully
        Adds a tag to Action Network. Once created, tags CANNOT be edited or deleted.
        """
        data = {
            "name": name
        }
        return self._add_entry("tags", data, silent)
