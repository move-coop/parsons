import requests
import json
from time import time
from parsons import Table


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

    def _get_entry_list(self, object_name, limit=10, timeout=60):
        # returns a list of entries for a given object, such as people, tags, or actions
        count = 0
        page = 1
        t0 = time()
        return_list = []
        while True:
            if page == 1:
                response = requests.get(url="%s/%s" % (self.api_url, object_name),
                                        headers=self.headers)
            else:
                response = requests.get(url="%s/%s?page=%d" % (self.api_url, object_name, page),
                                        headers=self.headers)
            page = page + 1
            response_list = response.json()['_embedded']['osdi:%s' % object_name]
            if not response_list:
                return Table(return_list)
            return_list.extend(response_list)
            count = count + len(response_list)
            if limit:
                if count >= limit:
                    return Table(return_list[0:limit])
            if time() - t0 > timeout:
                print("Request timed out. Returning results so far.")
                return Table(return_list)

    def _get_entry(self, object_name, object_id):
        # returns a specific entry by object name and id
        response = requests.get(url="%s/%s/%s" % (self.api_url, object_name, object_id),
                                headers=self.headers)
        return response.json()

    def _add_entry(self, object_name, data, verbose=False):
        # adds an entry to action network
        response = requests.post(url='%s/%s' % (self.api_url, object_name),
                                 data=json.dumps(data), headers=self.headers)
        if 'error' in response.json().keys():
            print('ERROR: %s' % response.json()['error'])
        elif verbose:
            identifiers = response.json()['identifiers']
            entry_id = [entry_id.split(':')[1]
                        for entry_id in identifiers if 'action_network:' in entry_id][0]
            print("Entry %s successfully added to %s" % (entry_id, object_name))

    def _delete_entry(self, object_name, entry_id, verbose=False):
        # deletes an entry
        response = requests.delete(url='%s/%s/%s' % (self.api_url, object_name, entry_id),
                                   headers=self.headers)
        if 'error' in response.json().keys():
            print('ERROR: %s' % response.json()['error'])
        elif verbose:
            print("Entry %s successfully added to %s" % (entry_id, object_name))

    def _update_entry(self, object_name, entry_id, data, verbose=False):
        # updates fields for a given entry
        # only the fields to be updated need to be included
        response = requests.pur(url='%s/%s/%s' % (self.api_url, object_name, entry_id),
                                data=json.dumps(data), headers=self.headers)
        if 'error' in response.json().keys():
            print('ERROR: %s' % response.json()['error'])
        elif verbose:
            print("%s entry %s successfully updated" % (object_name.capitalize(), entry_id))

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

    def add_person(self, email_address, given_name, family_name, tags=[],
                   languages_spoken=[], postal_addresses=[],
                   verbose=False, **kwargs):
        """
        `Args:`
            email_address:
                Can be any of the following
                    - a string, if the person has only one email address on file
                    - a list of string, if the person has multiple addresses on file
                    - a list dictionaries with the following fields
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
                Optional field. A list of strings of the person's postal addresses
            verbose:
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
        self._add_entry("people", data, verbose)

    def delete_person(self, entry_id, verbose=False):
        """
        `Args:`
            entry_id:
                The person's Action Network id
            verbose:
                If true, prints to the person's Action Network id when deleted successfully
        Deletes a person from Action Network
        """
        self._delete_entry("people", entry_id, verbose)

    def update_person(self, entry_id, verbose=False, **kwargs):
        """
        `Args:`
            entry_id:
                The person's Action Network id
            **kwargs:
                Fields to be updated.
        Updates a person's data in Action Network
        """
        data = {**kwargs}
        self._update_entry("people", entry_id, data, verbose)

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

    def add_tag(self, name, verbose=False):
        """
        `Args:`
            name:
                The tag's name. This is the ONLY editable field
            verbose:
                If true, prints to the person's Action Network id when added successfully
        Adds a tag to Action Network. Once created, tags CANNOT be edited or deleted.
        """
        data = {
            "name": name
        }
        self._add_entry("tags", data, verbose)
