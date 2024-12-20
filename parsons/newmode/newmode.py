from parsons.utilities.api_connector import APIConnector
from parsons.utilities.oauth_api_connector import OAuth2APIConnector
from parsons.utilities import check_env
from parsons import Table
import logging
import time

logger = logging.getLogger(__name__)

API_URL_V1 = "https://engage.newmode.net/api/"
API_URL_V2 = "https://base.newmode.net/api/"
API_AUTH_URL = "https://base.newmode.net/oauth/token/"
API_CAMPAIGNS_V2_URL = "https://base.newmode.net/"


class Newmode(object):
    """
    Instantiate Class
    `Args`:
        api_user: str
            The username to use for the API requests. Not required if ``NEWMODE_API_URL``
            env variable set.
        api_password: str
            The password to use for the API requests. Not required if ``NEWMODE_API_PASSWORD``
            env variable set.
        api_version: str
            The api version to use. Defaults to v1.0
    Returns:
        NewMode Class
    """

    def __init__(
        self,
        api_user=None,
        api_password=None,
        client_id=None,
        client_secret=None,
        api_version="v1.0",
    ):
        self.api_version = check_env.check("NEWMODE_API_VERSION", api_version)
        # TODO: delete when v1 depreciated
        if "v1" in self.api_version:
            logger.warning(
                "Newmode API v1 will no longer be supported starting Feburary 2025."
            )
            self.base_url = API_URL_V1
            self.api_user = check_env.check("NEWMODE_API_USER", api_user)
            self.api_password = check_env.check("NEWMODE_API_PASSWORD", api_password)
            self.headers = {"Content-Type": "application/json"}
            self.client = APIConnector(
                self.base_url,
                auth=(self.api_user, self.api_password),
                headers=self.headers,
            )
        else:
            self.base_url = API_URL_V2
            self.client_id = check_env.check("NEWMODE_API_CLIENT_ID", client_id)
            self.__client_secret = check_env.check(
                "NEWMODE_API_CLIENT_SECRET", client_secret
            )
            self.headers = {"content-type": "application/x-www-form-urlencoded"}

    def convert_to_table(self, data):
        """Internal method to create a Parsons table from a data element."""

        table = None
        if type(data) is list:
            table = Table(data)
        else:
            table = Table([data])

        return table

    # TODO: delete when v1 deprecated
    def base_request(
        self, method, url, requires_csrf=True, data=None, json=None, params={}
    ):
        if requires_csrf:
            csrf = self.get_csrf_token()
            self.headers["X-CSRF-Token"] = csrf

        response = None
        if method == "GET":
            response = self.client.get_request(url=url, params=params)
        elif method == "PATCH":
            response = self.client.patch_request(url=url, params=params)
        elif method == "POST":
            response = self.client.post_request(
                url=url, params=params, json=json, data=data
            )
        return response

    def base_request_v2(self, method, url, data=None, json=None, params={}):
        response = None
        if method == "GET":
            response = self.client.get_request(url=url, params=params)
        elif method == "PATCH":
            response = self.client.patch_request(url=url, params=params)
        elif method == "POST":
            response = self.client.post_request(
                url=url, params=params, json=json, data=data
            )
        return response

    # TODO: delete when v1 deprecated
    def converted_request(
        self,
        endpoint,
        method,
        requires_csrf=True,
        supports_version=True,
        data=None,
        json=None,
        params={},
        convert_to_table=True,
    ):
        url = f"{self.api_version}/{endpoint}" if supports_version else endpoint
        response = self.base_request(
            method=method,
            url=url,
            requires_csrf=requires_csrf,
            json=json,
            data=data,
            params=params,
        )
        if not response:
            logging.warning(f"Empty result returned from endpoint: {endpoint}")
        if convert_to_table:
            return self.convert_to_table(response)
        else:
            return response

    def converted_request_v2(
        self,
        endpoint,
        method,
        supports_version=True,
        data=None,
        json=None,
        params={},
        convert_to_table=True,
    ):
        self.client = OAuth2APIConnector(
            uri=self.base_url,
            auto_refresh_url=API_AUTH_URL,
            client_id=self.client_id,
            client_secret=self.__client_secret,
            headers=self.headers,
            token_url=API_AUTH_URL,
            grant_type="client_credentials",
        )
        
        url = f"{self.api_version}/{endpoint}" if supports_version else endpoint
        response = self.base_request_v2(
            method=method,
            url=url,
            json=json,
            data=data,
            params=params,
        )
        if not response:
            logging.warning(f"Empty result returned from endpoint: {endpoint}")
        if convert_to_table:
            return self.convert_to_table(response)
        else:
            return response

    # TODO:delete when v1 deprecated
    def get_csrf_token(self, max_retries=10):
        """
        Retrieve a CSRF token for making API requests
        `Args:`
            max_retries: int
                The maximum number of attempts to get the CSRF token.
        `Returns:`
            The CSRF token.
        """
        endpoint = "session/token"
        for attempt in range(max_retries):
            try:
                response = self.converted_request(
                    endpoint=endpoint,
                    method="GET",
                    supports_version=False,
                    requires_csrf=False,
                    convert_to_table=False,
                )
                return response["X-CSRF-Token"]
            except Exception as e:
                if attempt >= max_retries:
                    logger.error(
                        (f"Error getting CSRF Token after {max_retries} retries")
                    )
                    raise e
                logger.warning(
                    f"Retry {attempt} at getting CSRF Token failed. Retrying. Error: {e}"
                )
                time.sleep(attempt + 1)

    # def get_csrf_token_v2(self, max_retries=10):
    #     """
    #     Retrieve a CSRF token for making API requests
    #     `Args:`
    #         max_retries: int
    #             The maximum number of attempts to get the CSRF token.
    #     `Returns:`
    #         The CSRF token.
    #     """
    #     endpoint = "/user/login?_format=json"
    #     for attempt in range(max_retries):
    #         # try:
    #         response = self.converted_request_v2(
    #             endpoint=endpoint,
    #             method="POST",
    #             supports_version=False,
    #             convert_to_table=False,
    #         )
    #         print(response)
            #     return response
            # except Exception as e:
            #     if attempt >= max_retries:
            #         logger.error(
            #             (f"Error getting CSRF Token after {max_retries} retries")
            #         )
            #         raise e
            #     logger.warning(
            #         f"Retry {attempt} at getting CSRF Token failed. Retrying. Error: {e}"
            #     )
            #     time.sleep(attempt + 1)

    def get_tools(self, params={}):
        """
        V1 only
        Retrieve all tools
        `Args:`
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Parsons Table containing tools data.
        """
        response = self.converted_request(endpoint="tool", method="GET", params=params)
        return response

    def get_tool(self, tool_id, params={}):
        """
        V1 only
        Retrieve a specific tool by ID
        `Args:`
            tool_id: str
                The ID of the tool to retrieve.
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Parsons Table containing the tool data.
        """
        response = self.converted_request(
            endpoint=f"tool/{tool_id}", method="GET", params=params
        )
        return response

    def lookup_targets(self, target_id, search=None, location=None, params={}):
        """
        V1 only
        Lookup targets for a given tool
        `Args:`
            tool_id: str
                The ID of the tool to lookup targets for.
            search: str
                The search criteria (optional).
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Parsons Table containing target data.
        """
        endpoint = f"lookup/{target_id}"
        if search:
            endpoint += f"/{search}"
        if location:
            endpoint += f"/{location}"
        response = self.converted_request(
            endpoint=endpoint, method="GET", params=params
        )
        return response

    def get_action(self, tool_id, params={}):
        """
        V1 only
        Get action information for a specific tool
        `Args:`
            tool_id: str
                The ID of the tool to get action information for.
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Parsons Table containing action data.
        """
        response = self.converted_request(
            endpoint=f"action/{tool_id}", method="GET", params=params
        )
        return response

    def run_action(self, tool_id, payload, params={}):
        """
        V1 only
        Run a specific action for a tool
        `Args:`
            tool_id: str
                The ID of the tool to run the action for.
            payload: dict
                The data to post to run the action.
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Parsons Table containing posted outreach information.
        """
        response = self.converted_request(
            endpoint=f"action/{tool_id}", method="PATCH", payload=payload, params=params
        )
        return response

    def get_campaigns(self, params={}):
        """
        V1
        Retrieve all campaigns
        `Args:`
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Parsons Table containing campaigns data.
        """
        endpoint = "campaign"
        requires_csrf = True
        response = self.converted_request(
            endpoint=endpoint, method="GET", params=params, requires_csrf=requires_csrf
        )
        return response

    def get_campaign(self, campaign_id, params={}):
        """
        V1
        Retrieve a specific campaign by ID.

        `Args:`
            campaign_id: str
                The ID of the campaign to retrieve.
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Parsons Table containing campaign data.
        """
        endpoint = f"campaign/{campaign_id}"
        requires_csrf = True
        response = self.converted_request(
            endpoint=endpoint, method="GET", params=params, requires_csrf=requires_csrf
        )
        return response

    def get_organizations(self, params={}):
        """
        V1 only
        Retrieve all organizations
        `Args:`
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Parsons Table containing organizations data.
        """
        response = self.converted_request(
            endpoint="organization", method="GET", params=params
        )
        return response

    def get_organization(self, organization_id, params={}):
        """
        V1 only
        Retrieve a specific organization by ID
        `Args:`
            organization_id: str
                The ID of the organization to retrieve.
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Parsons Table containing organization data.
        """
        response = self.converted_request(
            endpoint=f"organization/{organization_id}", method="GET", params=params
        )
        return response

    def get_services(self, params={}):
        """
        V1 only
        Retrieve all services
        `Args:`
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Parsons Table containing services data.
        """
        response = self.converted_request(
            endpoint="service", method="GET", params=params
        )
        return response

    def get_service(self, service_id, params={}):
        """
        V1 only
        Retrieve a specific service by ID
        `Args:`
            service_id: str
                The ID of the service to retrieve.
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Parsons Table containing service data.
        """
        response = self.converted_request(
            endpoint=f"service/{service_id}", method="GET", params=params
        )
        return response

    def get_target(self, target_id, params={}):
        """
        V1 only
        Get specific target.
        `Args:`
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Parsons Table containing targets data.
        """
        response = self.converted_request(
            endpoint=f"target/{target_id}", method="GET", params=params
        )
        return response

    def get_targets(self, params={}):
        """
        V1 only
        Retrieve all targets
        `Args:`
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Parsons Table containing targets data.
        """
        response = self.converted_request(
            endpoint="target", method="GET", params=params
        )
        return response

    def get_outreaches(self, tool_id, params={}):
        """
        V1 only
        Retrieve all outreaches for a specific tool
        `Args:`
            tool_id: str
                The ID of the tool to get outreaches for.
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Parsons Table containing outreaches data.
        """
        params["nid"] = str(tool_id)
        response = self.converted_request(
            endpoint="outreach", method="GET", requires_csrf=False, params=params
        )
        return response

    def get_outreach(self, outreach_id, params={}):
        """
        V1 only
        Retrieve a specific outreach by ID
        `Args:`
            outreach_id: str
                The ID of the outreach to retrieve.
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Parsons Table containing outreach data.
        """
        response = self.converted_request(
            endpoint=f"outreach/{outreach_id}", method="GET", params=params
        )
        return response

    def get_campaign_v2(self, campaign_id, params={}):
        """
        V2
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
        response = self.converted_request_v2(
            endpoint=endpoint,
            method="GET",
            params=params,
        )
        return response

    def get_campaigns_v2(self, organization_id, params={}):
        """
        V2
        Retrieve all campaigns
        In v2, a campaign is equivalent to Tools or Actions in V1.
        `Args:`
            organization_id: str
                ID of organization
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Parsons Table containing campaigns data.
        """
        self.base_url = API_CAMPAIGNS_V2_URL
        self.api_version = "jsonapi"
        self.headers = {
            "content-type": "application/vnd.api+json",
            "accept": "application/vnd.api+json",
            "authorization": "Bearer 1234567890",
        }
        endpoint = f"action/action?filter[field_org_id]={organization_id}"
        response = self.converted_request_v2(
            endpoint=endpoint,
            method="GET",
            params=params,
        )
        return response

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
        V2 only
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
        if all(x is None for x in address_params.values()):
            logger.error(
                "Please specify a street address, city, postal code, and/or region."
            )
            raise Exception("Incomplete Request")

        params = {
            f"address[value][{key}]": value
            for key, value in address_params.items()
            if value
        }
        response = self.converted_request_v2(
            endpoint=f"campaign/{campaign_id}/target",
            method="GET",
            params=params,
        )
        return response

    # TODO: add run_submit method
    # def run_submit(self, campaign_id, json=None, data=None, params={}):
    #     """
    #     V2 only
    #     Pass a submission from a supporter to a campaign
    #     that ultimately fills in a petition,
    #     sends an email or triggers a phone call
    #     depending on your campaign type

    #     `Args:`
    #         campaign_id: str
    #             The ID of the campaign to retrieve.
    #         params: dict
    #             Query parameters to include in the request.
    #     `Returns:`
    #         Parsons Table containing submit data.
    #     """
    #     # json["action_id"] = campaign_id
    #     self.api_version = 2.0
    #     response = self.converted_request(
    #         endpoint=f"action/{campaign_id}/submit/?_format=json",
    #         method="POST",
    #         data=data,
    #         json=json,
    #         params=params,
    #         requires_csrf=False,
    #         convert_to_table=False,
    #     )
    #     return response

    def get_submissions(self, params={}):
        """
        V2 only
        Retrieve and sort submission and contact data
        for your organization using a range of filters
        that include campaign id, data range and submission status

        `Args:`
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Parsons Table containing submit data.
        """
        # self.base_url = API_AUTH_URL
        # print(self.base_url)
        # response=self.converted_request_v2(endpoint="/user/login?_format=json", method="POST", supports_version=False)
        # self.token = self.token['access_token']
        response = self.converted_request_v2(
            endpoint="submission", method="GET", params=params
        )
        return response
