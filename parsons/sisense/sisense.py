import json
import requests
import logging

from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector
from parsons.etl import Table

logger = logging.getLogger(__name__)

URI = 'https://app.periscopedata.com/api/v1/'


class Sisense(object):
    """
    Instantiate the Sisense class.

    `Args:`
        site_name: str
            The name of the site. Not required if the ``SISENSE_SITE_NAME``
            environmental variable is set.
        api_key: str
            The Sisense API Key. Not required if the ``SISENSE_API_KEY``
            environmental variable is set.
    `Returns:`
        Sisense class
    """

    def __init__(self, site_name=None, api_key=None):
        self.site_name = check_env.check('SISENSE_SITE_NAME', site_name)
        self.api_key = check_env.check('SISENSE_API_KEY', api_key)
        self.uri = URI
        self.api = self._api()

    def _api(self):
        headers = {'HTTP-X-PARTNER-AUTH': self.site_name + ":" + self.api_key}
        return APIConnector(uri=self.uri, headers=headers)

    def _create_dashboard_url(self, payload):
        """
        This method generates a dashboard URL following the approach described in the
        `Sisense Support guide <https://support.sisense.com/hc/en-us/community/posts/360038329993-Embed-URL-Generation-Made-Easy-With-Python-Script>`_ # noqa
        This allows the Sisense API to create the URL from a JSON blob,
        which is less error prone than creating the URL manually.

        `Args:`
            payload: dict
                A JSON blob defining the dashboard to publish.
        `Returns:`
            A URL or an error.
        """
        response = self.api.post_request('shared_dashboard/create', data=json.dumps(payload))
        try:
            return response['url']
        except KeyError as error:
            logger.error('Failed to generate embedded dashboard URL.')
            raise error

    def get_dashboards(self, dashboard_id=None, params=None):
        """
        `Args:`
            dashboard_id: int or str
                The dashboard ID. If no dashboard ID is provided, all dashboards
                for the user are returned.
            params: dict
                Request parameters. Check the `Sisense API documentation <https://sisense.dev/reference/rest/v1.html>`_ for options. # noqa
        `Returns:`
            A Table or an error.
        """
        if dashboard_id is None:
            response = self.api.get_request('dashboards', params=params)
        else:
            response = list(self.api.get_request(f'dashboards/{dashboard_id}', params=params))
        return Table(response)

    def get_dashboard_shares(self, dashboard_id, share_id=None, params=None):
        """
        `Args:`
            dashboard_id: int or str (required)
                The dashboard ID.
            share_id: int or str
                The share ID. If no share ID is provided, all shares
                for the dashboard are returned.
            params: dict
                Request parameters. Check the `Sisense API documentation <https://sisense.dev/reference/rest/v1.html>`_ for options. # noqa
        `Returns:`
            A Table or an error.
        """
        if share_id is None:
            response = self.api.get_request(f'dashboards/{dashboard_id}/shares', params=params)
        else:
            response = list(self.api.get_request(f'dashboards/{dashboard_id}/shares/{share_id}',
                                                 params=params))
        return Table(response)

    def publish_dashboard(self, dashboard_id, chart_id=None, **kwargs):
        """
        This method publishes a dashboard or chart using the provided arguments.
        For available options, see the `API documentation <https://dtdocs.sisense.com/article/embed-api-options>`_. # noqa

        `Args:`
            dashboard_id: str or int
                The ID of the dashboard (required).
            chart_id: str or int
                The ID of the chart. Only required for publishing individual charts.
            **kwargs:
                Optional arguments.
        `Returns:`
            Dashboard URL as a string or an error
        """
        payload = {'dashboard': dashboard_id, 'chart': chart_id, **kwargs}
        return self._create_dashboard_url(payload)
