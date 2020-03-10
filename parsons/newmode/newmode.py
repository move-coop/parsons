from Newmode import Client
from parsons.utilities import check_env, json_format
from parsons.etl import Table
import logging

logger = logging.getLogger(__name__)


class Newmode:
    """
    `Args:`
        api_user: str
            The Newmode api user. Not required if ``NEWMODE_API_USER`` env variable is
            passed.
        api_password: str
            The Newmode api password. Not required if ``NEWMODE_API_PASSWORD`` env variable is
            passed.
        api_version: str
            The Newmode api version. Defaults to "v1.0" or the value of ``NEWMODE_API_VERSION``
            env variable.
    `Returns`:
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

    def getTools(self):
        tools = self.client.getTools()
        if (tools):
            return self.convertToTable(tools)
        else:
            logging.warning("Empty tools returned")
            return []

    def getTool(self, tool_id):
        tool = self.client.getTool(tool_id)
        if (tool):
            return self.convertToTable(tool)
        else:
            logging.warning("Empty tool returned")
            return []

    """
    Lookup targets for a given tool
    `Args:`
        tool_id:
            The tool to lookup targets.
        search:
            The search criteria. It could be:
            - Empty: If empty, return custom targets associated to the tool.
            - Postal code: Return targets matched by postal code.
            - Lat/Long: Latitude and Longitude pair separated by '::'.
              Ex. 45.451596::-73.59912099999997. It will return targets
              matched for those coordinates.
            - Address: In format thoroughfare::locality::administrative_area::country
              It will return targets matched by the given address.
            - Search term: For your csv tools, this will return targets
              matched by given valid search term.
    `Returns:`
        Targets information.
    """

    def lookupTargets(self, tool_id, search=None):
        targets = self.client.lookupTargets(tool_id, search)
        if (targets):
            data = []
            for key in targets:
                if (key != '_links'):
                    data.append(targets[key])
            return self.convertToTable(data)
        else:
            logging.warning("Empty targets returned")
            return []

    def getAction(self, tool_id):
        action = self.client.getAction(tool_id)
        if (action):
            return self.convertToTable(action)
        else:
            logging.warning("Empty action returned")
            return []

    def runAction(self, tool_id, payload):
        action = self.client.runAction(tool_id, payload)
        if (action):
            return action.sid
        else:
            logging.warning("Error in response")
            return []

    def getTarget(self, target_id):
        target = self.client.getTarget(target_id)
        if (target):
            return self.convertToTable(target)
        else:
            logging.warning("Empty target returned")
            return []

    def getCampaigns(self):
        campaigns = self.client.getCampaigns()
        if (campaigns):
            return self.convertToTable(campaigns)
        else:
            logging.warning("Empty campaigns returned")
            return []

    def getCampaign(self, campaign_id):
        campaign = self.client.getCampaign(campaign_id)
        if (campaign):
            return self.convertToTable(campaign)
        else:
            logging.warning("Empty campaign returned")
            return []

    def getOrganizations(self):
        organizations = self.client.getOrganizations()
        if (organizations):
            return self.convertToTable(organizations)
        else:
            logging.warning("Empty organizations returned")
            return []

    def getOrganization(self, organization_id):
        organization = self.client.getOrganization(organization_id)
        if (organization):
            return self.convertToTable(organization)
        else:
            logging.warning("Empty organization returned")
            return []

    def getServices(self):
        services = self.client.getServices()
        if (services):
            return self.convertToTable(services)
        else:
            logging.warning("Empty services returned")
            return []

    def getService(self, service_id):
        service = self.client.getService(service_id)
        if (service):
            return self.convertToTable(service)
        else:
            logging.warning("Empty service returned")
            return []

    def getOutreaches(self, tool_id):
        outreaches = self.client.getOutreaches(tool_id)
        if (outreaches):
            return self.convertToTable(outreaches)
        else:
            logging.warning("Empty outreaches returned")
            return []

    def getOutreach(self, outreach_id):
        outreach = self.client.getOutreach(outreach_id)
        if (outreach):
            return self.convertToTable(outreach)
        else:
            logging.warning("Empty outreach returned")
            return []