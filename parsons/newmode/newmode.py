from Newmode import Client
from parsons.utilities import check_env, json_format
from parsons.etl import Table
import logging

logger = logging.getLogger(__name__)


class Newmode:
    """
    Args:
        api_user: str
            The Newmode api user. Not required if ``NEWMODE_API_USER`` env variable is
            passed.
        api_password: str
            The Newmode api password. Not required if ``NEWMODE_API_PASSWORD`` env variable is
            passed.
        api_version: str
            The Newmode api version. Defaults to "v1.0" or the value of ``NEWMODE_API_VERSION``
            env variable.
    Returns:
        Newmode class
    """

    def __init__(self, api_user=None, api_password=None, api_version=None):

        self.api_user = check_env.check('NEWMODE_API_USER', api_user)
        self.api_password = check_env.check('NEWMODE_API_PASSWORD', api_password)

        if (api_version == None):
            api_version = "v1.0"

        self.api_version = check_env.check('NEWMODE_API_VERSION', api_version)


        self.client = Client(api_user, api_password, api_version)

    def convertToTable(self, data):
        # Internal method to create a Parsons table from a data element.
        table = None
        if (type(data) is list):
            table = Table(data)
        else:
            table = Table([data])

        return table

    def getTools(self, params = {}):
        tools = self.client.getTools(params=params)
        if (tools):
            return self.convertToTable(tools)
        else:
            logging.warning("Empty tools returned")
            return []

    def getTool(self, tool_id, params = {}):
        tool = self.client.getTool(tool_id, params=params)
        if (tool):
            return self.convertToTable(tool)
        else:
            logging.warning("Empty tool returned")
            return []

    """
    Lookup targets for a given tool
    Args:
        tool_id:
            The tool to lookup targets.
        search:
            The search criteria. It could be:
            - Empty: If empty, return custom targets associated to the tool.
            - Postal code: Return targets matched by postal code.
            - Lat/Long: Latitude and Longitude pair separated by '::'.
              Ex. 45.451596::-73.59912099999997. It will return targets
              matched for those coordinates.
            - Search term: For your csv tools, this will return targets
              matched by given valid search term.
    Returns:
        Targets information.
    """

    def lookupTargets(self, tool_id, search=None, params = {}):
        targets = self.client.lookupTargets(tool_id, search, params=params)
        if (targets):
            data = []
            for key in targets:
                if (key != '_links'):
                    data.append(targets[key])
            return self.convertToTable(data)
        else:
            logging.warning("Empty targets returned")
            return []

    def getAction(self, tool_id, params = {}):
        action = self.client.getAction(tool_id, params=params)
        if (action):
            return self.convertToTable(action)
        else:
            logging.warning("Empty action returned")
            return []

    def runAction(self, tool_id, payload, params = {}):
        action = self.client.runAction(tool_id, payload, params=params)
        if (action):
            if ('link' in action):
                return action['link']
            else:
                return action['sid']
        else:
            logging.warning("Error in response")
            return []

    def getTarget(self, target_id, params = {}):
        target = self.client.getTarget(target_id, params=params)
        if (target):
            return self.convertToTable(target)
        else:
            logging.warning("Empty target returned")
            return []

    def getCampaigns(self, params = {}):
        campaigns = self.client.getCampaigns(params=params)
        if (campaigns):
            return self.convertToTable(campaigns)
        else:
            logging.warning("Empty campaigns returned")
            return []

    def getCampaign(self, campaign_id, params = {}):
        campaign = self.client.getCampaign(campaign_id, params=params)
        if (campaign):
            return self.convertToTable(campaign)
        else:
            logging.warning("Empty campaign returned")
            return []

    def getOrganizations(self, params = {}):
        organizations = self.client.getOrganizations(params=params)
        if (organizations):
            return self.convertToTable(organizations)
        else:
            logging.warning("Empty organizations returned")
            return []

    def getOrganization(self, organization_id, params = {}):
        organization = self.client.getOrganization(organization_id, params=params)
        if (organization):
            return self.convertToTable(organization)
        else:
            logging.warning("Empty organization returned")
            return []

    def getServices(self, params = {}):
        services = self.client.getServices(params=params)
        if (services):
            return self.convertToTable(services)
        else:
            logging.warning("Empty services returned")
            return []

    def getService(self, service_id, params = {}):
        service = self.client.getService(service_id, params=params)
        if (service):
            return self.convertToTable(service)
        else:
            logging.warning("Empty service returned")
            return []

    def getOutreaches(self, tool_id, params = {}):
        outreaches = self.client.getOutreaches(tool_id, params=params)
        if (outreaches):
            return self.convertToTable(outreaches)
        else:
            logging.warning("Empty outreaches returned")
            return []

    def getOutreach(self, outreach_id, params = {}):
        outreach = self.client.getOutreach(outreach_id, params=params)
        if (outreach):
            return self.convertToTable(outreach)
        else:
            logging.warning("Empty outreach returned")
            return []