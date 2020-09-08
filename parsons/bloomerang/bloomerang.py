import json
import requests
import logging

from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector
from parsons.etl import Table

logger = logging.getLogger(__name__)

URI = "https://api.bloomerang.co/v2/"
URI_AUTH = "https://crm.bloomerang.co/authorize/"


class Bloomerang(object):
    """
    Instantiate Bloomerang class

    `Args:`
        api_key: str
            The Bloomerang API key. Not required if the ``BLOOMERANG_API_KEY`` environmental
            variable is set or if the OAuth2 authentication parameters ``client_id`` and
            ``client_secret`` are set.
        client_id: str
            The Bloomerang client ID for OAuth2 authentication. Not required if
            the ``BLOOMERANG_CLIENT_ID`` env variable is set or if the ``api_key``
            parameter is set. Note that the ``client_secret`` parameter must
            also be set in order to use OAuth2 authentication.
        client_secret: str
            The Bloomerang client secret for OAuth2 authetication. Not required if
            the ``BLOOMERANG_CLIENT_SECRET`` env variable is set or if the ``api_key``
            parameter is set. Note that the ``client_id`` parameter must
            also be set in order to use OAuth2 authentication.
    """

    def __init__(self, api_key=None, client_id=None, client_secret=None):
        self.api_key = check_env.check('BLOOMERANG_API_KEY', api_key, optional=True)
        self.client_id = check_env.check('BLOOMERANG_CLIENT_ID', client_id, optional=True)
        self.client_secret = check_env.check('BLOOMERANG_CLIENT_SECRET', client_secret,
                                             optional=True)
        self.uri = URI
        self.uri_auth = URI_AUTH
        self.conn = self._conn()

    def _conn(self):
        # Instantiate APIConnector with authentication credentials
        headers = {"accept": "application/json",
                   "Content-Type": "application/json"}
        if self.api_key is not None:
            logger.info("Using API key authentication.")
            headers['X-API-KEY'] = f"{self.api_key}"
        elif (self.client_id is not None) & (self.client_secret is not None):
            logger.info('Using OAuth2 authentication.')
            self._generate_authorization_code()
            self._generate_access_token()
            headers['Authorization'] = f"Bearer {self.access_token}"
        else:
            logger.warning('Initializing API Connector without authorization credentials.')
        return APIConnector(uri=self.uri, headers=headers)

    def _generate_authorization_code(self):
        data = {'client_id': self.client_id,
                'response_type': 'code'}
        r = requests.post(url=self.uri_auth, json=data)
        self.authorization_code = r.json().get('code', None)

    def _generate_access_token(self):
        data = {'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'authorization_code',
                'code': self.authorization_code}
        r = requests.post(url=self.uri + 'oauth/token', json=data)
        self.access_token = r.json().get('access_token', None)

    def _base_endpoint(self, endpoint, entity_id=None):
        url = f'{self.uri}{endpoint}/'
        if entity_id:
            url = url + f'{entity_id}/'
        return url

    def _base_create(self, endpoint, entity_id=None, **kwargs):
        return self.conn.post_request(url=self._base_endpoint(endpoint, entity_id),
                                      json=json.dumps({**kwargs}))

    def _base_update(self, endpoint, entity_id=None, **kwargs):
        return self.conn.put_request(url=self._base_endpoint(endpoint, entity_id),
                                     json=json.dumps({**kwargs}))

    def _base_get(self, endpoint, entity_id=None):
        return self.conn.get_request(url=self._base_endpoint(endpoint, entity_id))

    def _base_delete(self, endpoint, entity_id=None):
        return self.conn.delete_request(url=self._base_endpoint(endpoint, entity_id))

    def create_constituent(self, **kwargs):
        """
        `Args:`
            **kwargs:`
                Fields to include, e.g., FirstName = 'Rachel'
        """
        return self._base_create('constituent', **kwargs)

    def update_constituent(self, constituent_id, **kwargs):
        """
        `Args:`
            constituent_id:
                Constituent ID to update
            **kwargs:`
                Fields to update, e.g., FirstName = 'RJ'
        """
        return self._base_update('constituent', entity_id=constituent_id, **kwargs)

    def get_constituent(self, constituent_id):
        """
        `Args:`
            constituent_id:
                Constituent ID to get fields for
        `Returns:`
            A  JSON of the entry or an error.
        """
        return self._base_get('constituent', entity_id=constituent_id)

    def delete_constituent(self, constituent_id):
        """
        `Args:`
            constituent_id:
                Constituent ID to delete
        """
        return self._base_delete('constituent', entity_id=constituent_id)

    def get_constituents(self, constituent_ids):
        """
        `Args:`
            constituent_ids:
                A list of Constituent IDs to get fields for
        `Returns:`
            A Table of the entries.
        """
        query_params = '?skip=0&take=50&id=' + '|'.join([str(c_id) for c_id in constituent_ids])
        return Table(self._base_get(f'constituents{query_params}')['Results'])

    def create_transaction(self, **kwargs):
        """
        `Args:`
            **kwargs:`
                Fields to include, e.g., CreditCardType = 'Visa'
        """
        return self._base_create('transaction', **kwargs)

    def update_transaction(self, transaction_id, **kwargs):
        """
        `Args:`
            transaction_id:
                Transaction ID to update
            **kwargs:`
                Fields to update, e.g., CreditCardType = 'Visa'
        """
        return self._base_update('transaction', entity_id=transaction_id, **kwargs)

    def get_transaction(self, transaction_id):
        """
        `Args:`
            transaction_id:
                Transaction ID to get fields for
        `Returns:`
            A  JSON of the entry or an error.
        """
        return self._base_get('transaction', entity_id=transaction_id)

    def delete_transaction(self, transaction_id):
        """
        `Args:`
            transaction_id:
                Transaction ID to delete
        """
        return self._base_delete('transaction', entity_id=transaction_id)

    def get_transactions(self, transaction_ids):
        """
        `Args:`
            transaction_ids:
                A list of Transaction IDs to get records for
        `Returns:`
            A  JSON of the entry or an error.
        """
        query_params = '?skip=0&take=50&id=' + '|'.join([str(t_id) for t_id in transaction_ids])
        return Table(self._base_get(f'transactions{query_params}')['Results'])

    def get_transaction_designation(self, designation_id):
        """
        `Args:`
            designation_id:
                Transaction Designation ID to get fields for
        `Returns:`
            A  JSON of the entry or an error.
        """
        return self._base_get('transaction/designation', entity_id=designation_id)

    def get_transaction_designations(self, designation_ids):
        """
        `Args:`
            designation_ids:
                A list of Designation IDs to get records for
        `Returns:`
            A  JSON of the entry or an error.
        """
        query_params = '?skip=0&take=50&id=' + '|'.join([str(d_id) for d_id in designation_ids])
        return Table(self._base_get(f'transactions/designations{query_params}')['Results'])

    def create_interaction(self, **kwargs):
        """
        `Args:`
            **kwargs:`
                Fields to include, e.g., Channel = "Email"
        """
        return self._base_create('interaction', **kwargs)

    def update_interaction(self, interaction_id, **kwargs):
        """
        `Args:`
            interaction_id:
                Interaction ID to update
            **kwargs:`
                Fields to update, e.g., EmailAddress = "user@example.com"
        """
        return self._base_update('interaction', entity_id=interaction_id, **kwargs)

    def get_interaction(self, interaction_id):
        """
        `Args:`
            interaction_id:
                Interaction ID to get fields for
        `Returns:`
            A  JSON of the entry or an error.
        """
        return self._base_get('interaction', entity_id=interaction_id)

    def delete_interaction(self, interaction_id):
        """
        `Args:`
            interaction_id:
                Interaction ID to delete
        """
        return self._base_delete('interaction', entity_id=interaction_id)

    def get_interactions(self, interaction_ids):
        """
        `Args:`
            interaction_ids:
                A list of Interaction IDs to get records for
        `Returns:`
            A  JSON of the entry or an error.
        """
        query_params = '?skip=0&take=50&id=' + '|'.join([str(i_id) for i_id in interaction_ids])
        return Table(self._base_get(f'interactions{query_params}')['Results'])
