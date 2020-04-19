import requests
import json
from time import time

class ActionNetwork(object):
    """
    `Args:`
        api_token: str
            The OSDI API token
        api_url:
            The end point url
    """
    def __init__(self, api_token, api_url):
        self.headers = {
            "Content-Type": "application/json",
            "OSDI-API-Token": api_token
        }
        self.api_url = api_url
    def get_entry_list(self, object_name, limit=10, timeout=60):
        """
        `Args:`
            object_name: str
                The name of the object you wish to query (examples: 'people', 'tags')
            limit:
                The number of entries to return. When None, returns all entries.
            timeout:
                Seconds before request is forced to timeout. Implemented to ensur no infinite loops.
        `Returns:`
            A list of JSONs of entries stored in Action Network. For example, when querying
            'people' returns of list of all people and their properties.
        """
        count = 0
        page = 1
        t0 = time()
        return_list = []
        while True:
            if page == 1:
                response = requests.get(url="%s/%s" % (self.api_url, object_name), headers=self.headers)
            else:
                response = requests.get(url="%s/%s?page=%d" % (self.api_url, object_name, page), headers=self.headers)
            page = page + 1
            response_list = response.json()['_embedded']['osdi:%s' % object_name]
            if not response_list:
                return return_list
            return_list.extend(response_list)
            count = count + len(response_list)
            if limit:
                if count >= limit:
                    return return_list[0:limit]
            if time() - t0 > timeout:
                print("Request timed out. Returning results so far.")
                return return_list
    def get_entry(self, object_name, object_id):
        """
        `Args:`
            object_name: str
                The name of the object you wish to query (examples: 'people', 'tags')
            object_id:
                Id of the entry.
        `Returns:`
            A  JSON of the entry. If the entry doesn't exist, Action Network returns
            "{'error': 'Couldn't find <object_name> with id = <id>'}"
        """
        response = requests.get(url="%s/%s/%s" % (self.api_url, object_name, object_id), headers=self.headers)
        return response.json()
    def add_entry(self, object_name, data, verbose=False):
        """
        `Args:`
            object_name: str
                The name of the object you wish to query (examples: 'people', 'tags')
            data:
                A dictionary of information to be stored on the entry.
        """
        response = requests.post(url='%s/%s' % (self.api_url, object_name), \
                                 data=json.dumps(data), headers=self.headers)
        if 'error' in response.json().keys():
            print('ERROR: %s' % response.json()['error'])
        elif verbose:
            identifiers = response.json()['identifiers']
            entry_id = [entry_id.split(':')[1] for entry_id in identifiers if 'action_network:' in entry_id][0]
            print("Entry %s successfully added to %s" % (entry_id, object_name))
    def get_people_list(self, limit, timeout=60):
        """
        `Args:`
            limit:
                The number of entries to return. When None, returns all entries.
            timeout:
                Seconds before request is forced to timeout. Implemented to ensur no infinite loops.
        `Returns:`
            A list of JSONs of people stored in Action Network.
        """
        self.get_entry_list(self, "people", limit, timeout)
    def get_person(self, object_id):
        """
        `Args:`
            object_id:
                Id of the entry.
        `Returns:`
            A  JSON of the entry. If the entry doesn't exist, Action Network returns
            "{'error': 'Couldn't find <object_name> with id = <id>'}"
        """
        self.get_entry("people", object_id)
    def add_person(email_address, tags=[], verbose=False, **kwargs):
        data = {
            "person" : {
                "email_addresses" : [ { "address" : email_address}],
                **kwargs
              },
              "add_tags": tags
            }
        self.add_entry(people, data, verbose)