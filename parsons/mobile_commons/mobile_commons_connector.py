"""Mobile Commons Connector."""

import requests
import os
import xmltodict
import json
import logging
from parsons.etl.table import Table

logger = logging.getLogger(__name__)


class MobileCommonsConnector(object):
    """Mobile Commons Connector Class."""

    def __init__(self, username=None, password=None, company=None,
                 uri='https://secure.mcommons.com/api/'):
        """Initialize the MobileCommonsConnector class.

        `Args:`
            username: str
                The username for a mobile commons account with API permissions.
                If it's not passed in, it will attempt to get it from the
                environement, MC_USER.
            password: str
                The password associated with the username. If it's not passed
                in, it will attempt to get it from the environement, MC_PASS.
            company: str
                Specify which account/company you want to use for this session.
                If you leave it off, your default account will be used.
            uri: str
                Base uri to make api calls.
        """
        if username is None:

            try:
                username = os.environ['MC_USER']
            except KeyError:
                raise KeyError('No Mobile Commons username found. Store as '
                               'MC_USER environment variable or pass as an '
                               'argument.')

        if password is None:

            try:
                password = os.environ['MC_PASS']
            except KeyError:
                raise KeyError('No Mobile Commons password found. Store as '
                               'MC_PASS environment variable or pass as an '
                               'argument.')

        self.uri = uri
        self.username = username
        self.password = password
        self.company = company

    def request(self, url, req_type='GET', post_data=None, args=None,
                raw=False, resp_type='json'):
        """Send a request - internal."""
        auth = (self.username, self.password)

        if self.company:
            if not args:
                args = {}
            args['company'] = self.company

        if req_type == 'GET':
            r = requests.get(url, auth=auth, params=args)

        if req_type == 'POST':
            r = requests.post(url, auth=auth, json=post_data, params=args)

        if req_type == 'PATCH':
            r = requests.patch(url, auth=auth, json=post_data, params=args)

        if req_type == 'PUT':
            r = requests.put(url, auth=auth, json=post_data, params=args)

        if req_type == 'DELETE':
            r = requests.delete(url, auth=auth, params=args)

        # TODO: Parse all of the errors and stuff.

        if raw:

            return r

        else:
            if resp_type == 'xml':
                result = json.loads(json.dumps(xmltodict.parse(r.text)))
                return self.clean_dict(result)
            else:
                return r.json()

    def request_paginate(self, url, rsrc, req_type='GET', post_data=None,
                         args=None, resp_type='json'):
        """Paginate through request - internal."""
        items = []
        next_page = True
        rsrc_s = rsrc[:-1]

        counter = None
        count = 0

        while next_page:

            i = self.request(url, req_type=req_type, post_data=post_data,
                             args=args, resp_type=resp_type)

            if not counter:
                if i['response'][rsrc].get('num'):
                    counter = 'num'
                else:
                    counter = 'page_count'

            if int(i['response'][rsrc][counter]) == 0:
                next_page = False
                break

            items.extend(i['response'][rsrc][rsrc_s])

            args['page'] = int(i['response'][rsrc]['page']) + 1

            count += int(i['response'][rsrc][counter])

            if args.get('limit') and count >= args['limit']:
                next_page = False
                break

        return items

    def clean_dict(self, d, rem='@'):
        """Recursively remove a string from the keys if a dictself.

        `Args:`
            d: list or dict
                The list or dict to be cleaned.
            rem: str
                The string to remove from the key.
        `Returns:`
            list or dict depending on the input
        """
        if isinstance(d, list):
            newl = []
            for e in d:
                if isinstance(e, dict):
                    newl.append(self.clean_dict(e))
                else:
                    newl.append(e)
            return newl

        else:
            new = {}

            for k, v in d.items():
                if isinstance(v, dict):
                    v = self.clean_dict(v)

                if isinstance(v, list):
                    newl = []
                    for e in v:
                        if isinstance(e, dict):
                            newl.append(self.clean_dict(e))
                        else:
                            newl.append(e)
                    new[k.replace(rem, '')] = newl
                    continue

                new[k.replace(rem, '')] = v
            return new

    def output(self, list_obj):
        """Return an object as a Table.

        `Args:`
            list_obj: dict or list
                The list or dict to be output.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """
        if isinstance(list_obj, dict):
            list_obj = [list_obj]

        return Table(list_obj)
