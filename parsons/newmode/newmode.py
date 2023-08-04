from Newmode import Client
from parsons.utilities import check_env
from parsons.etl import Table
import logging

logger = logging.getLogger(__name__)


class Newmode:
    def __init__(self, api_user=None, api_password=None, api_version=None):
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
        self.api_user = check_env.check("NEWMODE_API_USER", api_user)
        self.api_password = check_env.check("NEWMODE_API_PASSWORD", api_password)

        if api_version is None:
            api_version = "v1.0"

        self.api_version = check_env.check("NEWMODE_API_VERSION", api_version)

        self.client = Client(api_user, api_password, api_version)

    def convert_to_table(self, data):
        # Internal method to create a Parsons table from a data element.
        table = None
        if type(data) is list:
            table = Table(data)
        else:
            table = Table([data])

        return table

    def get_tools(self, params={}):
        """
        Get existing tools.
        Args:
            params:
                Extra parameters sent to New/Mode library.
        Returns:
            Tools information as table.
        """
        tools = self.client.getTools(params=params)
        if tools:
            return self.convert_to_table(tools)
        else:
            logging.warning("Empty tools returned")
            return self.convert_to_table([])

    def get_tool(self, tool_id, params={}):
        """
        Get specific tool.
        Args:
            tool_id:
                The id of the tool to return.
            params:
                Extra parameters sent to New/Mode library.
        Returns:
            Tool information.
        """
        tool = self.client.getTool(tool_id, params=params)
        if tool:
            return tool
        else:
            logging.warning("Empty tool returned")
            return None

    def lookup_targets(self, tool_id, search=None, params={}):
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
            Targets information as table.
        """
        targets = self.client.lookupTargets(tool_id, search, params=params)
        if targets:
            data = []
            for key in targets:
                if key != "_links":
                    data.append(targets[key])
            return self.convert_to_table(data)
        else:
            logging.warning("Empty targets returned")
            return self.convert_to_table([])

    def get_action(self, tool_id, params={}):
        """
        Get the action information for a given tool.
        Args:
            tool_id:
                The id of the tool to return.
            params:
                Extra parameters sent to New/Mode library.
        Returns:
            Tool action information.
        """
        action = self.client.getAction(tool_id, params=params)
        if action:
            return action
        else:
            logging.warning("Empty action returned")
            return None

    def run_action(self, tool_id, payload, params={}):
        """
        Run specific action with given payload.
        Args:
            tool_id:
                The id of the tool to run.
            payload:
                Payload data used to run the action. Structure will depend
                on the stuff returned by get_action.
            params:
                Extra parameters sent to New/Mode library.
        Returns:
            Action link (if otl) or sid.
        """
        action = self.client.runAction(tool_id, payload, params=params)
        if action:
            if "link" in action:
                return action["link"]
            else:
                return action["sid"]
        else:
            logging.warning("Error in response")
            return None

    def get_target(self, target_id, params={}):
        """
        Get specific target.
        Args:
            target_id:
                The id of the target to return.
            params:
                Extra parameters sent to New/Mode library.
        Returns:
            Target information.
        """
        target = self.client.getTarget(target_id, params=params)
        if target:
            return target
        else:
            logging.warning("Empty target returned")
            return None

    def get_targets(self, params={}):
        """
        Get all targets

        Args:
            params dict:
                Extra paramaters sent to New/Mode library

        Returns:
            Target information
        """

        targets = self.client.getTargets(params=params)

        if targets:
            return self.convert_to_table(targets)

        else:
            logging.warning("No targets returned")
            return None

    def get_campaigns(self, params={}):
        """
        Get existing campaigns.
        Args:
            params:
                Extra parameters sent to New/Mode library.
        Returns:
            Campaigns information as table.
        """
        campaigns = self.client.getCampaigns(params=params)
        if campaigns:
            return self.convert_to_table(campaigns)
        else:
            logging.warning("Empty campaigns returned")
            return self.convert_to_table([])

    def get_campaign(self, campaign_id, params={}):
        """
        Get specific campaign.
        Args:
            campaign_id:
                The id of the campaign to return.
            params:
                Extra parameters sent to New/Mode library.
        Returns:
            Campaign information.
        """
        campaign = self.client.getCampaign(campaign_id, params=params)
        if campaign:
            return campaign
        else:
            logging.warning("Empty campaign returned")
            return None

    def get_organizations(self, params={}):
        """
        Get existing organizations.
        Args:
            params:
                Extra parameters sent to New/Mode library.
        Returns:
            Organizations information as table.
        """
        organizations = self.client.getOrganizations(params=params)
        if organizations:
            return self.convert_to_table(organizations)
        else:
            logging.warning("Empty organizations returned")
            return self.convert_to_table([])

    def get_organization(self, organization_id, params={}):
        """
        Get specific organization.
        Args:
            organization_id:
                The id of the organization to return.
            params:
                Extra parameters sent to New/Mode library.
        Returns:
            Organization information.
        """
        organization = self.client.getOrganization(organization_id, params=params)
        if organization:
            return organization
        else:
            logging.warning("Empty organization returned")
            return None

    def get_services(self, params={}):
        """
        Get existing services.
        Args:
            params:
                Extra parameters sent to New/Mode library.
        Returns:
            Services information as table.
        """
        services = self.client.getServices(params=params)
        if services:
            return self.convert_to_table(services)
        else:
            logging.warning("Empty services returned")
            return self.convert_to_table([])

    def get_service(self, service_id, params={}):
        """
        Get specific service.
        Args:
            service_id:
                The id of the service to return.
            params:
                Extra parameters sent to New/Mode library.
        Returns:
            Service information.
        """
        service = self.client.getService(service_id, params=params)
        if service:
            return service
        else:
            logging.warning("Empty service returned")
            return None

    def get_outreaches(self, tool_id, params={}):
        """
        Get existing outreaches for a given tool.
        Args:
            tool_id:
                Tool to return outreaches.
            params:
                Extra parameters sent to New/Mode library.
        Returns:
            Outreaches information as table.
        """
        outreaches = self.client.getOutreaches(tool_id, params=params)
        if outreaches:
            return self.convert_to_table(outreaches)
        else:
            logging.warning("Empty outreaches returned")
            return self.convert_to_table([])

    def get_outreach(self, outreach_id, params={}):
        """
        Get specific outreach.
        Args:
            outreach_id:
                The id of the outreach to return.
            params:
                Extra parameters sent to New/Mode library.
        Returns:
            Outreach information.
        """
        outreach = self.client.getOutreach(outreach_id, params=params)
        if outreach:
            return outreach
        else:
            logging.warning("Empty outreach returned")
            return None
