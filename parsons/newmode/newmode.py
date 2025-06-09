import logging

from Newmode import Client

from parsons.etl import Table
from parsons.utilities import check_env
from parsons.utilities.oauth_api_connector import OAuth2APIConnector

logger = logging.getLogger(__name__)

V2_API_URL = "https://base.newmode.net/api/"
V2_API_AUTH_URL = "https://base.newmode.net/oauth/token/"
V2_API_CAMPAIGNS_URL = "https://base.newmode.net/"
V2_API_CAMPAIGNS_VERSION = "jsonapi"
V2_API_CAMPAIGNS_HEADERS = {
    "content-type": "application/vnd.api+json",
    "accept": "application/vnd.api+json",
    "authorization": "Bearer 1234567890",
}


class NewmodeV1:
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
        logger.warning(
            "Newmode V1 API will be sunset in Feburary 28th, 2025. To use V2, set api_version=v2.1"
        )
        self.api_user = check_env.check("NEWMODE_API_USER", api_user)
        self.api_password = check_env.check("NEWMODE_API_PASSWORD", api_password)
        self.api_version = api_version
        self.client = Client(api_user, api_password, api_version)

    def convert_to_table(self, data):
        # Internal method to create a Parsons table from a data element.
        table = None
        if isinstance(data, list):
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


class NewmodeV2:
    # TODO: Add param definition and requirements once official Newmode docs are published
    def __init__(
        self,
        client_id=None,
        client_secret=None,
        api_version="v2.1",
    ):
        """
        Instantiate Class
        `Args`:
            client_id: str
                The client id to use for the API requests. Not required if ``NEWMODE_API_CLIENT_ID``
                env variable set.
            client_secret: str
                The client secret to use for the API requests. Not required if ``NEWMODE_API_CLIENT_SECRET``
                env variable set.
            api_version: str
                The api version to use. Defaults to v2.1
        Returns:
            NewMode Class
        """
        self.api_version = api_version
        self.base_url = V2_API_URL
        self.client_id = check_env.check("NEWMODE_API_CLIENT_ID", client_id)
        self.client_secret = check_env.check("NEWMODE_API_CLIENT_SECRET", client_secret)
        self.headers = {"content-type": "application/json"}
        self.default_client = OAuth2APIConnector(
            uri=self.base_url,
            auto_refresh_url=V2_API_AUTH_URL,
            client_id=self.client_id,
            client_secret=self.client_secret,
            headers=self.headers,
            token_url=V2_API_AUTH_URL,
            grant_type="client_credentials",
        )

    def base_request(
        self,
        method,
        endpoint,
        client,
        data=None,
        json=None,
        data_key=None,
        params={},
        supports_version=True,
        override_api_version=None,
    ):
        """
        Internal method to instantiate OAuth2APIConnector class,
        make a call to Newmode API, and validate the response.
        """
        api_version = override_api_version if override_api_version else self.api_version
        url = f"{api_version}/{endpoint}" if supports_version else endpoint
        response = client.request(url=url, req_type=method, json=json, data=data, params=params)
        response.raise_for_status()
        success_codes = [200, 201, 202, 204]
        client.validate_response(response)
        if response.status_code in success_codes:
            response_json = response.json() if client.json_check(response) else None
            return response_json[data_key] if data_key and response_json else response_json
        raise Exception(f"API request encountered an error. Response: {response}")

    def converted_request(
        self,
        endpoint,
        method,
        supports_version=True,
        data=None,
        json=None,
        params={},
        convert_to_table=True,
        data_key=None,
        client=None,
        override_api_version=None,
    ):
        """Internal method to make a call to the Newmode API and convert the result to a Parsons table."""

        client = client if client else self.default_client
        response = self.base_request(
            method=method,
            json=json,
            data=data,
            params=params,
            data_key=data_key,
            supports_version=supports_version,
            endpoint=endpoint,
            client=client,
            override_api_version=override_api_version,
        )
        if response:
            if convert_to_table:
                return client.convert_to_table(data=response)
            else:
                return response

    def get_campaign(self, campaign_id, params={}):
        """
        Retrieve a specific campaign by ID.

        In v2, a campaign is equivalent to Tools or Actions in V1.
        `Args:`
            campaign_id: str
                The ID of the campaign to retrieve.
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Parsons Table containing campaign data.
        """
        endpoint = f"/campaign/{campaign_id}/form"
        data = self.converted_request(
            endpoint=endpoint,
            method="GET",
            params=params,
        )
        return data

    def get_campaign_ids(self, params={}):
        """
        Retrieve all campaigns
        In v2, a campaign is equivalent to Tools or Actions in V1.
        `Args:`
            organization_id: str
                ID of organization
            params: dict
                Query parameters to include in the request.
        `Returns:`
            List containing all campaign ids.
        """
        endpoint = "node/action"
        campaigns_client = OAuth2APIConnector(
            uri=V2_API_CAMPAIGNS_URL,
            auto_refresh_url=V2_API_AUTH_URL,
            client_id=self.client_id,
            client_secret=self.client_secret,
            headers=V2_API_CAMPAIGNS_HEADERS,
            token_url=V2_API_AUTH_URL,
            grant_type="client_credentials",
        )

        data = self.converted_request(
            endpoint=endpoint,
            method="GET",
            params=params,
            data_key="data",
            client=campaigns_client,
            override_api_version=V2_API_CAMPAIGNS_VERSION,
        )
        return data["id"]

    def get_recipient(
        self,
        campaign_id,
        street_address=None,
        city=None,
        postal_code=None,
        region=None,
        params={},
    ):
        """
        Retrieve a specific recipient by ID
        `Args:`
            campaign_id: str
                The ID of the campaign to retrieve.
            street_address: str
                Street address of recipient
            city: str
                City of recipient
            postal_code: str
                Postal code of recipient
            region: str
                Region (i.e. state/province abbreviation) of recipient
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Parsons Table containing recipient data.
        """
        address_params = {
            "street_address": street_address,
            "city": city,
            "postal_code": postal_code,
            "region": region,
        }
        all_address_params_are_missing = all(x is None for x in address_params.values())
        if all_address_params_are_missing:
            raise ValueError(
                "Incomplete Request. Please specify a street address, city, postal code, and/or region."
            )

        params = {f"address[value][{key}]": value for key, value in address_params.items() if value}
        response = self.converted_request(
            endpoint=f"campaign/{campaign_id}/target",
            method="GET",
            params=params,
        )
        return response

    def run_submit(self, campaign_id, json=None, data=None, params={}):
        """
        Pass a submission from a supporter to a campaign
        that ultimately fills in a petition,
        sends an email or triggers a phone call
        depending on your campaign type

        `Args:`
            campaign_id: str
                The ID of the campaign to retrieve.
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Parsons Table containing submit data.
        """

        response = self.converted_request(
            endpoint=f"campaign/{campaign_id}/submit",
            method="POST",
            data=data,
            json=json,
            params=params,
            convert_to_table=False,
        )
        return response

    def get_submissions(self, campaign_id, params={}):
        """
        Retrieve and sort submissions and contact data
        for a specified campaign using a range of filters
        that include campaign id, data range and submission status

        `Args:`
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Parsons Table containing submit data.
        """
        params = {"action": campaign_id}
        response = self.converted_request(endpoint="submission", method="GET", params=params)
        return response


class Newmode:
    def __new__(
        cls,
        client_id=None,
        client_secret=None,
        api_user=None,
        api_password=None,
        api_version="v1.0",
    ):
        """
        Create and return Newmode instance based on chosen version (V1 or V2)

        `Args`:
            api_user: str
                The Newmode api user. Not required if ``NEWMODE_API_USER`` env variable is
                passed. Needed for V1.
            api_password: str
                The Newmode api password. Not required if ``NEWMODE_API_PASSWORD`` env variable is
                passed. Needed for V1.
            client_id: str
                The client id to use for the API requests. Not required if ``NEWMODE_API_CLIENT_ID``
                env variable set. Needed for V2.
            client_secret: str
                The client secret to use for the API requests. Not required if ``NEWMODE_API_CLIENT_SECRET``
                env variable set. Needed for V2.
            api_version: str
                The api version to use. Defaults to v1.0.

        Returns:
            NewMode Class
        """
        api_version = check_env.check("NEWMODE_API_VERSION", api_version)
        if api_version.startswith("v2"):
            return NewmodeV2(
                client_id=client_id, client_secret=client_secret, api_version=api_version
            )
        if api_version.startswith("v1"):
            return NewmodeV1(api_user=api_user, api_password=api_password, api_version=api_version)
        raise ValueError(f"{api_version} not supported.")
