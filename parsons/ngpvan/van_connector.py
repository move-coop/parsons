from requests import request as _request
from suds.client import Client
from parsons.etl.table import Table
import logging
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector

logger = logging.getLogger(__name__)

URI = 'https://api.securevan.com/v4/'
SOAP_URI = 'https://api.securevan.com/Services/V3/ListService.asmx?WSDL'


class VANConnector(object):

    def __init__(self, api_key=None, auth_name='default', db=None):

        self.api_key = check_env.check('VAN_API_KEY', api_key)

        if db == 'MyVoters':
            self.db_code = 0
        elif db in ['MyMembers', 'MyCampaign', 'EveryAction']:
            self.db_code = 1
        else:
            raise KeyError('Invalid database type specified. Pick one of:'
                           ' MyVoters, MyCampaign, MyMembers, EveryAction.')

        self.uri = URI
        self.db = db
        self.auth_name = auth_name
        self.auth = (self.auth_name, self.api_key + '|' + str(self.db_code))

        # Standardized API Connector.
        self.api = APIConnector(self.uri, auth=self.auth, data_key='items')

        # We will not create the SOAP client unless we need to as this triggers checking for
        # valid credentials. As not all API keys are provisioned for SOAP, this keeps it from
        # raising a permission exception when creating the class.
        self._soap_client = None

    @property
    def soap_client(self):

        if not self._soap_client:

            # Create the SOAP client
            soap_auth = {'Header': {'DatabaseMode': self.db, 'APIKey': self.api_key}}
            self._soap_client = Client(SOAP_URI, soapheaders=soap_auth)

        return self._soap_client

    def get_request(self, endpoint, **kwargs):

        r = self.api.get_request(self.uri + endpoint, **kwargs)
        data = self.api.data_parse(r)

        # Paginate
        while self.api.next_page_check_url(r):
            r = self.api.get_request(r[self.pagination_key], **kwargs)
            data.extend(self.api.data_parse(r))

        return data

    def post_request(self, endpoint, **kwargs):

        return self.api.post_request(self.uri + endpoint, **kwargs)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Below is all of the old code that will be replaced in future PRs. However, it works #
    # for the time being, so we are going to keep it.                                     #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def _error_check(self, r):

        if r.status_code == 404:

            # To Do: Make the errors prettier...
            logger.info(f"{r.status_code} Error: {r.json()['errors']}")

            return r.json()['errors']

        else:

            logger.debug(f'{r.json()}')
            return r.json()

    def request(self, url, req_type='GET', post_data=None, args=None, raw=False, paginate=False):
        # Internal request function

        r = _request(req_type, url, auth=self.auth, json=post_data, params=args)

        """
        # To Do: Figure out if this is still needed.
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logging.info(err)
            if self.raise_for_status:
                r.raise_for_status()
        """

        if req_type in ['POST', 'DELETE', 'PUT'] or (req_type == 'GET' and r.status_code != 200):
            return self.code_parse(r)

        if raw:
            # Commenting out for the moment
            # return self._error_check(r)
            return r

        elif paginate:
            return r.json()

        else:
            if len(r.text) == 0:
                data = []
            elif isinstance(r.json(), list):
                data = r.json()
            else:
                data = [r.json()]

            if not data:
                logging.warning('No data returned in table.')

            return Table(data)

    def request_paginate(self, url, req_type='GET', post_data=None, args=None):
        # Internal request function that paginates

        items = []
        next_page = True

        while next_page:

            i = self.request(url, req_type=req_type, post_data=post_data, args=args, paginate=True)

            if 'count' not in i or i['count'] == 0:
                return Table(items)

            items.extend(i['items'])

            if not i['nextPageLink']:
                next_page = False

            url = i['nextPageLink']

        return Table(items)

    def api_test(self):

        url = self.uri + 'echoes/'
        r = self.request(url, req_type="POST", post_data={'message': 'True'})
        if r['message'] == 'True':
            return True
        else:
            return False

    def code_parse(self, req_obj):

        if req_obj.status_code == 200 and len(req_obj.text) == 0:
            return (200, 'OK')

        elif req_obj.status_code == 204:
            return (204, 'No Content')

        elif req_obj.status_code == 404:
            return (404, 'Not Found')

        elif req_obj.status_code in [400, 403, 500]:
            return (int(req_obj.status_code), req_obj.json())

        else:
            return req_obj.json()
