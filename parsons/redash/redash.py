import json
import logging
import requests
import time

from parsons.etl.table import Table
from parsons.utilities.check_env import check

logger = logging.getLogger(__name__)


class RedashTimeout(Exception):
    pass


class RedashQueryFailed(Exception):
    pass


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

    def __init__(
        self,
        base_url=None,
        user_api_key=None,
        pause_time=3,
        timeout=0,  # never timeout
        verify=True,
    ):
        self.base_url = check("REDASH_BASE_URL", base_url)
        self.user_api_key = check("REDASH_USER_API_KEY", user_api_key, optional=True)
        self.pause = int(check("REDASH_PAUSE_TIME", pause_time, optional=True))
        self.timeout = int(check("REDASH_TIMEOUT", timeout, optional=True))

        self.verify = verify  # for https requests
        self.session = requests.Session()
        if user_api_key:
            self.session.headers.update({"Authorization": f"Key {user_api_key}"})

    def _catch_runtime_error(self, res):
        if res.status_code != 200:
            raise RuntimeError(f"Error. Status code: {res.status_code}. Reason: {res.reason}")

    def _poll_job(self, session, job, query_id):
        start_secs = time.time()
        while job["status"] not in (3, 4):
            if self.timeout and start_secs + self.timeout < time.time():
                raise RedashTimeout(f"Redash timeout: {self.timeout}")
            poll_url = "{}/api/jobs/{}".format(self.base_url, job["id"])
            response = session.get(poll_url, verify=self.verify)
            response_json = response.json()
            job = response_json.get(
                "job",
                {"status": "Error NO JOB IN RESPONSE: {}".format(json.dumps(response_json))},
            )
            logger.debug(
                "poll url:%s id:%s status:%s err:%s",
                poll_url,
                query_id,
                job["status"],
                job.get("error"),
            )
            time.sleep(self.pause)

        if job["status"] == 3:  # 3 = completed
            return job["query_result_id"]
        elif job["status"] == 4:  # 3 = ERROR
            raise RedashQueryFailed("Redash Query {} failed: {}".format(query_id, job["error"]))

    def get_data_source(self, data_source_id):
        """
        Get a data source.

        `Args:`
            data_source_id: int or str
                ID of data source.
        `Returns`:
            Data source json object
        """
        res = self.session.get(f"{self.base_url}/api/data_sources/{data_source_id}")
        self._catch_runtime_error(res)
        return res.json()

    def update_data_source(self, data_source_id, name, type, dbName, host, password, port, user):
        """
        Update a data source.

        `Args:`
            data_source_id: str or int
                ID of data source.
            name: str
                Name of data source.
            type: str
                Type of data source.
            dbname: str
                Database name of data source.
            host: str
                Host of data source.
            password: str
                Password of data source.
            port: int or str
                Port of data source.
            user: str
                Username of data source.
        `Returns:`
            ``None``
        """
        self._catch_runtime_error(
            self.session.post(
                f"{self.base_url}/api/data_sources/{data_source_id}",
                json={
                    "name": name,
                    "type": type,
                    "options": {
                        "dbname": dbName,
                        "host": host,
                        "password": password,
                        "port": port,
                        "user": user,
                    },
                },
            )
        )

    def get_fresh_query_results(self, query_id=None, params=None):
        """
        Make a fresh query result and get back the CSV http response object back
        with the CSV string in result.content

        `Args:`
            query_id: str or int
                The query id of the query
            params: dict
                If there are values for the redash query parameters
                (described https://redash.io/help/user-guide/querying/query-parameters
                e.g. "{{datelimit}}" in the query),
                then this is a dict that will pass the parameters in the POST.
                We add the "p_" prefix for parameters, so if your query had ?p_datelimit=....
                in the url, you should just set 'datelimit' in params here.
                If you set this with REDASH_QUERY_PARAMS environment variable instead of passing
                the values, then you must include the "p_" prefixes and it should be a single
                url-encoded string as you would see it in the URL bar.
        `Returns:`
            Table Class
        """
        query_id = check("REDASH_QUERY_ID", query_id, optional=True)
        params_from_env = check("REDASH_QUERY_PARAMS", "", optional=True)
        redash_params = (
            {"p_%s" % k: str(v).replace("'", "''") for k, v in params.items()} if params else {}
        )

        response = self.session.post(
            f"{self.base_url}/api/queries/{query_id}/refresh?{params_from_env}",
            params=redash_params,
            verify=self.verify,
        )

        if response.status_code != 200:
            raise RedashQueryFailed(f"Refresh failed for query {query_id}. {response.text}")

        job = response.json()["job"]
        result_id = self._poll_job(self.session, job, query_id)
        if result_id:
            response = self.session.get(
                f"{self.base_url}/api/queries/{query_id}/results/{result_id}.csv",
                verify=self.verify,
            )
            if response.status_code != 200:
                raise RedashQueryFailed(
                    f"Failed getting results for query {query_id}. {response.text}"
                )
        else:
            raise RedashQueryFailed(f"Failed getting result {query_id}. {response.text}")
        return Table.from_csv_string(response.text)

    def get_cached_query_results(self, query_id=None, query_api_key=None):
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
            Table Class
        """
        query_id = check("REDASH_QUERY_ID", query_id)
        query_api_key = check("REDASH_QUERY_API_KEY", query_api_key, optional=True)
        params = {}
        if not self.user_api_key and query_api_key:
            params["api_key"] = query_api_key
        response = self.session.get(
            f"{self.base_url}/api/queries/{query_id}/results.csv",
            params=params,
            verify=self.verify,
        )
        if response.status_code != 200:
            raise RedashQueryFailed(f"Failed getting results for query {query_id}. {response.text}")
        return Table.from_csv_string(response.text)

    @classmethod
    def load_to_table(cls, refresh=True, **kwargs):
        """
        Fast classmethod makes the appropriate query type (refresh or cached)
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
        initargs = {
            a: kwargs.get(a)
            for a in ("base_url", "user_api_key", "pause_time", "timeout", "verify")
            if a in kwargs
        }
        obj = cls(**initargs)
        if not refresh or kwargs.get("query_api_key"):
            return obj.get_cached_query_results(kwargs.get("query_id"), kwargs.get("query_api_key"))
        else:
            return obj.get_fresh_query_results(kwargs.get("query_id"), kwargs.get("params"))
