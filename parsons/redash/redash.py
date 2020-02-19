import json
import logging
import requests
import time

from parsons.etl.table import Table

logger = logging.getLogger(__name__)


class Redash(object):
    """
    Instantiate Redash Class

    `Args:`
        base_url: str
            The base url for your redash instance (excluding the final /)
        user_api_key: str
            The user API key found in the User's profile screen
        pause_time int
            Specify time between polling for refreshed queries (Defaults to 3 seconds)
        verify: bool
            For https requests, should the certificate be verified (Defaults to True)
    `Returns:`
        Redash Class
    """
    args = {'base_url': None,
            'user_api_key': None,
            'pause_time': 3,
            'verify': True,
            'query_id': None,
            'params': None}

    def __init__(self,
                 base_url="http://localhost",
                 user_api_key=None,
                 pause_time=3,
                 verify=True):
        self.base_url = base_url
        self.user_api_key = user_api_key
        self.pause = pause_time   # seconds to delay
        self.verify = verify  # for https requests
        self.session = requests.Session()
        if user_api_key:
            self.session.headers.update({'Authorization': f'Key {user_api_key}'})

    def _poll_job(self, session, job, query_id):
        while job['status'] not in (3, 4):
            poll_url = '{}/api/jobs/{}'.format(self.base_url, job['id'])
            response = session.get(poll_url, verify=self.verify)
            response_json = response.json()
            job = response_json.get(
                'job',
                {'status': 'Error NO JOB IN RESPONSE: {}'.format(json.dumps(response_json))})
            logger.debug('poll', poll_url, query_id, job['status'], job.get('error'))
            time.sleep(self.pause)

        if job['status'] == 3:  # 3 = completed
            return job['query_result_id']
        elif job['status'] == 4:  # 3 = ERROR
            raise Exception('Redash Query {} failed: {}'.format(query_id, job['error']))

    def get_fresh_query_results(self, query_id, params=None):
        """
        Make a fresh query result and get back the CSV http response object back
        with the CSV string in result.content

        `Args:`
            query_id: str or int
                The query id of the query
            params: dict
                If there are parameters in the query (e.g. "{{datelimit}}" in the query),
                then this is a dict that will pass the parameters in the POST.
                We add the "p_" prefix for parameters, so if your query had ?p_datelimit=....
                in the url, you should just set 'datelimit' in params here.
        `Returns:`
            Response Class
        """
        redash_params = ({'p_%s' % k: str(v).replace("'", "''") for k, v in params.items()}
                         if params else {})

        response = self.session.post(f'{self.base_url}/api/queries/{query_id}/refresh',
                                     params=redash_params,
                                     verify=self.verify)

        if response.status_code != 200:
            raise Exception(f'Refresh failed for query {query_id}. {response.text}')

        job = response.json()['job']
        result_id = self._poll_job(self.session, job, query_id)
        if result_id:
            response = self.session.get(
                f'{self.base_url}/api/queries/{query_id}/results/{result_id}.csv',
                verify=self.verify)
            if response.status_code != 200:
                raise Exception(f'Failed getting results for query {query_id}. {response.text}')
        else:
            raise Exception(f'Failed getting result {query_id}. {response.text}')
        return response

    def get_cached_query_results(self, query_id, query_api_key=None):
        """
        Get the results from a cached query result and get back the CSV http response object back
        with the CSV string in result.content

        `Args:`
            query_id: str or int
                The query id of the query
            query_api_key: str
                If you did not supply a user_api_key on the Redash object, then you can
                supply a query_api_key to get cached results back anonymously.
        `Returns:`
            Response Class
        """
        params = {}
        if not self.user_api_key and query_api_key:
            params['api_key'] = query_api_key
        response = self.session.get(f'{self.base_url}/api/queries/{query_id}/results.csv',
                                    params=params,
                                    verify=self.verify)
        if response.status_code != 200:
            raise Exception(f'Failed getting results for query {query_id}. {response.text}')
        return response

    @classmethod
    def load_to_table(cls, refresh=True, **kwargs):
        """
        Fast classmethod so you can get the data all at once:
        tabledata = Redash.load_to_table(base_url='https://example.com', user_api_key='abc123',
                                         query_id=1001, params={'datelimit': '2020-01-01'})
        This instantiates the class and makes the appropriate query type (refresh or cached)
        based on which arguments are supplied.

        `Args:`
            base_url: str
                The base url for your redash instance (excluding the final /)
            query_id: str or int
                The query id of the query
            user_api_key: str
                The user API key found in the User's profile screen required for refresh queries
            query_api_key: str
                If you did not supply a user_api_key on the Redash object, then you can
                supply a query_api_key to get cached results back anonymously.
            pause_time int
                Specify time between polling for refreshed queries (Defaults to 3 seconds)
            verify: bool
                For https requests, should the certificate be verified (Defaults to True)
            refresh: bool
                Refresh results or cached. (Defaults to True unless a query_api_key IS supplied)
            params: dict
                For refresh queries, if there are parameters in the query,
                then this is a dict that will pass the parameters in the POST.
                We add the "p_" prefix for parameters, so if your query had ?p_datelimit=....
                in the url, you should just set 'datelimit' in params here.

        `Returns:`
            Table Class
        """
        initargs = {a: kwargs.get(a)
                    for a in ('base_url', 'user_api_key', 'pause_time', 'verify')
                    if a in kwargs}
        obj = cls(**initargs)
        res = None
        if not refresh or kwargs.get('query_api_key'):
            res = obj.get_cached_query_results(kwargs.get('query_id'), kwargs.get('query_api_key'))
        else:
            res = obj.get_fresh_query_results(kwargs.get('query_id'), kwargs.get('params'))
        return Table.from_csv_string(res.text)
