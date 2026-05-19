import logging
from typing import Any

from Newmode import Client
from oauthlib.oauth2 import TokenExpiredError

from parsons import Table
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

PAGINATION_NEXT = "next"
RESPONSE_DATA_KEY = "data"
RESPONSE_LINKS_KEY = "links"


class NewmodeV1:
    def __init__(
        self,
        api_user: str | None = None,
        api_password: str | None = None,
        api_version: str | None = None,
    ):
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

        """
        logger.warning(
            "Newmode V1 API will be sunset in Feburary 28th, 2025. To use V2, set api_version=v2.1"
        )
        self.api_user: str = check_env.check("NEWMODE_API_USER", api_user)
        self.api_password: str = check_env.check("NEWMODE_API_PASSWORD", api_password)
        self.api_version: str | None = api_version
        self.client: Client = Client(api_user, api_password, api_version)

    def convert_to_table(self, data: list[dict[str, Any]] | dict[str, Any]) -> Table:
        # Internal method to create a Parsons table from a data element.
        table = None
        table = Table(data) if isinstance(data, list) else Table([data])

        return table

    def get_tools(self, params: dict[str, Any] | None = None) -> Table:
        """
        Get existing tools.

        Args:
            params:
                Extra parameters sent to New/Mode library.

        Returns:
            Tools information as table.

        """
        if params is None:
            params = {}
        tools = self.client.getTools(params=params)
        if tools:
            return self.convert_to_table(tools)
        else:
            logging.warning("Empty tools returned")
            return self.convert_to_table([])

    def get_tool(
        self, tool_id: int | str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
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
        if params is None:
            params = {}
        tool = self.client.getTool(tool_id, params=params)
        if tool:
            return tool
        else:
            logging.warning("Empty tool returned")
            return None

    def lookup_targets(
        self,
        tool_id: int | str,
        search: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> Table:
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
        if params is None:
            params = {}
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

    def get_action(
        self, tool_id: int | str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
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
        if params is None:
            params = {}
        action = self.client.getAction(tool_id, params=params)
        if action:
            return action
        else:
            logging.warning("Empty action returned")
            return None

    def run_action(
        self,
        tool_id: int | str,
        payload: dict[str, Any],
        params: dict[str, Any] | None = None,
    ) -> str | int | None:
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
        if params is None:
            params = {}
        action = self.client.runAction(tool_id, payload, params=params)
        if action:
            if "link" in action:
                return action["link"]
            else:
                return action["sid"]
        else:
            logging.warning("Error in response")
            return None

    def get_target(
        self, target_id: int | str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
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
        if params is None:
            params = {}
        target = self.client.getTarget(target_id, params=params)
        if target:
            return target
        else:
            logging.warning("Empty target returned")
            return None

    def get_targets(self, params: dict[str, Any] | None = None) -> Table | None:
        """
        Get all targets

        Args:
            params dict:
                Extra paramaters sent to New/Mode library

        Returns:
            Target information

        """

        if params is None:
            params = {}
        targets = self.client.getTargets(params=params)

        if targets:
            return self.convert_to_table(targets)

        else:
            logging.warning("No targets returned")
            return None

    def get_campaigns(self, params: dict[str, Any] | None = None) -> Table:
        """
        Get existing campaigns.

        Args:
            params:
                Extra parameters sent to New/Mode library.

        Returns:
            Campaigns information as table.

        """
        if params is None:
            params = {}
        campaigns = self.client.getCampaigns(params=params)
        if campaigns:
            return self.convert_to_table(campaigns)
        else:
            logging.warning("Empty campaigns returned")
            return self.convert_to_table([])

    def get_campaign(
        self, campaign_id: int | str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
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
        if params is None:
            params = {}
        campaign = self.client.getCampaign(campaign_id, params=params)
        if campaign:
            return campaign
        else:
            logging.warning("Empty campaign returned")
            return None

    def get_organizations(self, params: dict[str, Any] | None = None) -> Table:
        """
        Get existing organizations.

        Args:
            params:
                Extra parameters sent to New/Mode library.

        Returns:
            Organizations information as table.

        """
        if params is None:
            params = {}
        organizations = self.client.getOrganizations(params=params)
        if organizations:
            return self.convert_to_table(organizations)
        else:
            logging.warning("Empty organizations returned")
            return self.convert_to_table([])

    def get_organization(
        self, organization_id: int | str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
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
        if params is None:
            params = {}
        organization = self.client.getOrganization(organization_id, params=params)
        if organization:
            return organization
        else:
            logging.warning("Empty organization returned")
            return None

    def get_services(self, params: dict[str, Any] | None = None) -> Table:
        """
        Get existing services.

        Args:
            params:
                Extra parameters sent to New/Mode library.

        Returns:
            Services information as table.

        """
        if params is None:
            params = {}
        services = self.client.getServices(params=params)
        if services:
            return self.convert_to_table(services)
        else:
            logging.warning("Empty services returned")
            return self.convert_to_table([])

    def get_service(
        self, service_id: int | str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
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
        if params is None:
            params = {}
        service = self.client.getService(service_id, params=params)
        if service:
            return service
        else:
            logging.warning("Empty service returned")
            return None

    def get_outreaches(self, tool_id: int | str, params: dict[str, Any] | None = None) -> Table:
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
        if params is None:
            params = {}
        outreaches = self.client.getOutreaches(tool_id, params=params)
        if outreaches:
            return self.convert_to_table(outreaches)
        else:
            logging.warning("Empty outreaches returned")
            return self.convert_to_table([])

    def get_outreach(
        self, outreach_id: int | str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
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
        if params is None:
            params = {}
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
        client_id: str | None = None,
        client_secret: str | None = None,
        api_version: str = "v2.1",
    ):
        """
        Instantiate Class
        Args:
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
        self.api_version: str = api_version
        self.base_url: str = V2_API_URL
        self.client_id: str = check_env.check("NEWMODE_API_CLIENT_ID", client_id)
        self.client_secret: str = check_env.check("NEWMODE_API_CLIENT_SECRET", client_secret)
        self.headers: dict[str, str] = {"content-type": "application/json"}
        self.default_client: OAuth2APIConnector = self.get_default_oauth_client()
        self.campaigns_client: OAuth2APIConnector = self.get_campaigns_oauth_client()

    def get_campaigns_oauth_client(self) -> OAuth2APIConnector:
        return OAuth2APIConnector(
            uri=V2_API_CAMPAIGNS_URL,
            auto_refresh_url=None,
            client_id=self.client_id,
            client_secret=self.client_secret,
            headers=V2_API_CAMPAIGNS_HEADERS,
            token_url=V2_API_AUTH_URL,
            grant_type="client_credentials",
        )

    def get_default_oauth_client(self) -> OAuth2APIConnector:
        return OAuth2APIConnector(
            uri=self.base_url,
            auto_refresh_url=None,
            client_id=self.client_id,
            client_secret=self.client_secret,
            headers=self.headers,
            token_url=V2_API_AUTH_URL,
            grant_type="client_credentials",
        )

    def checked_response(self, response: Any, client: OAuth2APIConnector) -> dict[str, Any] | None:
        response.raise_for_status()
        success_codes = [200, 201, 202, 204]
        client.validate_response(response)
        if response.status_code in success_codes:
            try:
                if client.json_check(response):
                    return response.json()
            except Exception:
                logger.error("Response is not in JSON format.")
        raise ValueError(f"API request encountered an error. Response: {response}")

    def base_request(
        self,
        method: str,
        url: str,
        retries: int = 2,
        use_campaigns_client: bool = False,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None | None:
        """
        Internal method to instantiate OAuth2APIConnector class,
        make a single call to Newmode API, and validate the response.
        """
        if params is None:
            params = {}

        if retries is None:
            retries = 2

        client = self.default_client if not use_campaigns_client else self.campaigns_client

        for attempt in range(retries + 1):
            try:
                try:
                    response = client.request(
                        url=url, req_type=method, json=json, data=data, params=params
                    )
                    return self.checked_response(response, client)
                except TokenExpiredError as e:
                    logger.warning(f"Token expired: {e}. Refreshing it...")
                    self.default_client = self.get_default_oauth_client()
                    self.campaigns_client = self.get_campaigns_oauth_client()
                    client = (
                        self.default_client if not use_campaigns_client else self.campaigns_client
                    )
            except Exception as e:
                if attempt < retries:
                    logger.warning(f"Request failed (attempt {attempt + 1}/{retries}). Retrying...")
                else:
                    logger.error(f"Request failed after {retries} retries.")
                    raise e
        raise Exception(f"Failed to retrieve data from {url} after {retries} attempts.")

    def paginate_request(
        self,
        method: str,
        endpoint: str,
        use_campaigns_client: bool = False,
        data_key: str = RESPONSE_DATA_KEY,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        supports_version: bool = True,
        override_api_version: str | None = None,
        retries: int = 2,
    ) -> list[dict[str, Any]]:
        """Wrapper method to handle pagination for API requests."""
        if params is None:
            params = {}
        results = []
        api_version = override_api_version if override_api_version else self.api_version
        url = f"{api_version}/{endpoint}" if supports_version else endpoint
        while url:
            response = self.base_request(
                method=method,
                url=url,
                use_campaigns_client=use_campaigns_client,
                data=data,
                json=json,
                params=params,
                retries=retries,
            )
            if data_key and response:
                data_to_add = response.get(data_key, [])
                if not isinstance(data_to_add, list):
                    data_to_add = [data_to_add]
                results.extend(data_to_add)
            else:
                results.append(response)
            # Check for pagination
            url = None
            if response:
                url = response.get(RESPONSE_LINKS_KEY, {}).get(PAGINATION_NEXT, {})
                if isinstance(url, dict):
                    url = url.get("href")

        return results

    def converted_request(
        self,
        endpoint: str,
        method: str,
        retries: int = 2,
        supports_version: bool = True,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        convert_to_table: bool = True,
        data_key: str | None = None,
        use_campaigns_client: bool = False,
        override_api_version: str | None = None,
    ) -> Table | dict[str, Any]:
        """Internal method to make a call to the Newmode API and convert the result to a Parsons table."""

        if params is None:
            params = {}
        response = self.paginate_request(
            method=method,
            json=json,
            data=data,
            params=params,
            data_key=data_key,
            supports_version=supports_version,
            endpoint=endpoint,
            use_campaigns_client=use_campaigns_client,
            override_api_version=override_api_version,
            retries=retries,
        )
        if response:
            if convert_to_table:
                return self.default_client.convert_to_table(data=response)
            else:
                return response

    def get_campaign(
        self,
        campaign_id: str,
        retries: int = 2,
        params: dict[str, Any] | None = None,
    ) -> Table:
        """
        Retrieve a specific campaign by ID.

        In v2, a campaign is equivalent to Tools or Actions in V1.

        Args:
            campaign_id: str
                The ID of the campaign to retrieve.
            params: dict
                Query parameters to include in the request.

        Returns:
            Parsons Table containing campaign data.

        """
        if params is None:
            params = {}
        endpoint = f"/campaign/{campaign_id}/form"
        data = self.converted_request(
            endpoint=endpoint, method="GET", params=params, retries=retries
        )
        return data

    def get_campaign_ids(
        self,
        retries: int = 2,
        params: dict[str, Any] | None = None,
    ) -> list[str]:
        """
        Retrieve all campaigns
        In v2, a campaign is equivalent to Tools or Actions in V1.

        Args:
            organization_id: str
                ID of organization
            params: dict
                Query parameters to include in the request.

        Returns:
            List containing all campaign ids.

        """
        if params is None:
            params = {}
        endpoint = "node/action"

        data = self.converted_request(
            endpoint=endpoint,
            method="GET",
            params=params,
            data_key=RESPONSE_DATA_KEY,
            use_campaigns_client=True,
            override_api_version=V2_API_CAMPAIGNS_VERSION,
            retries=retries,
        )
        return data["id"]

    def get_recipient(
        self,
        campaign_id: str,
        street_address: str | None = None,
        city: str | None = None,
        postal_code: str | None = None,
        region: str | None = None,
        params: dict[str, Any] | None = None,
        retries: int | None = None,
    ) -> Table:
        """
        Retrieve a specific recipient by ID

        Args:
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

        Returns:
            Parsons Table containing recipient data.

        """
        if params is None:
            params = {}
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
            endpoint=f"campaign/{campaign_id}/target", method="GET", params=params, retries=retries
        )
        return response

    def run_submit(
        self,
        campaign_id: str,
        retries: int = 2,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Pass a submission from a supporter to a campaign
        that ultimately fills in a petition,
        sends an email or triggers a phone call
        depending on your campaign type

        Args:
            campaign_id: str
                The ID of the campaign to retrieve.
            params: dict
                Query parameters to include in the request.

        Returns:
            Parsons Table containing submit data.

        """

        if params is None:
            params = {}
        response = self.converted_request(
            endpoint=f"campaign/{campaign_id}/submit",
            method="POST",
            data=data,
            json=json,
            params=params,
            convert_to_table=False,
            retries=retries,
        )
        return response[0]

    def get_submissions(
        self,
        campaign_id: str,
        retries: int = 2,
        params: dict[str, Any] | None = None,
    ) -> Table:
        """
        Retrieve and sort submissions and contact data
        for a specified campaign using a range of filters
        that include campaign id, data range and submission status

        Args:
            params: dict
                Query parameters to include in the request.

        Returns:
            Parsons Table containing submit data.

        """
        if params is None:
            params = {}
        params = {"action": campaign_id}
        response = self.converted_request(
            endpoint="submission",
            method="GET",
            params=params,
            data_key=RESPONSE_DATA_KEY,
            retries=retries,
        )
        return response


class Newmode:
    def __new__(
        cls,
        client_id: str | None = None,
        client_secret: str | None = None,
        api_user: str | None = None,
        api_password: str | None = None,
        api_version: str = "v1.0",
    ) -> NewmodeV1 | NewmodeV2:
        """
        Create and return Newmode instance based on chosen version (V1 or V2)

        Args:
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
                client_id=client_id,
                client_secret=client_secret,
                api_version=api_version,
            )
        if api_version.startswith("v1"):
            return NewmodeV1(api_user=api_user, api_password=api_password, api_version=api_version)
        raise ValueError(f"{api_version} not supported.")
