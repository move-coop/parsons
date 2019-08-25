"""Mobile Commons Campaings Endpoints."""


class Campaigns(object):
    """Class for campaigns endpoints."""

    def __init__(self, mc_connection):
        """Initialize the Campaigns class.

        `Args:`
            mc_connection: MobileCommonsConnector
                The connector to access the Mobile Commons API.
        """
        self.connection = mc_connection

    def campaigns(self, include_opt_in_paths=0, sort='asc', status=None,
                  campaign_id=None):
        """Return a list of campaigns.

        `Args:`
            include_opt_in_paths: int
                Set to 1 to include all opt-in path details. Default is 0.
            sort: str
                Set to `asc` or `desc` to sort by campaign ID ascending or
                descending. Default is ascending.
            status: str
                Set to active or ended to filter results. Default is empty and
                returns all campaigns.
            campaign_id: str
                Provide a specific campaign ID to view single result, invalid
                campaign ID will return all campaigns.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """
        url = self.connection.uri + 'campaigns'

        args = {'include_opt_in_paths': include_opt_in_paths,
                'sort': sort,
                'status': status,
                'campaign_id': campaign_id}

        response = self.connection.request(url, args=args, resp_type='xml')

        if response['response']['success'] == 'true':
            return self.connection.output(
                response['response']['campaigns']['campaign'])
        else:
            return None

    def campaign(self, campaign_id, include_opt_in_paths=0):
        """Return a single campaign.

        `Args:`
            campaign_id: str
                Provide a specific campaign ID to view single result, invalid
                campaign ID will return all campaigns.
            include_opt_in_paths: int
                Set to 1 to include all opt-in path details. Default is 0.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """
        url = self.connection.uri + 'campaigns'

        args = {'include_opt_in_paths': include_opt_in_paths,
                'campaign_id': campaign_id}

        response = self.connection.request(url, args=args, resp_type='xml')

        if response['response']['success'] == 'true':
            return self.connection.output(
                response['response']['campaigns']['campaign'])
        else:
            return None
