from parsons.utilities.api_connector import APIConnector
from parsons.utilities import check_env
import logging
import time

logger = logging.getLogger(__name__)

API_URL = "https://engage.newmode.net/api/"


class NewMode(object):
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
            The api version to use. Defaults to v2.1
    Returns:
        NewMode Class
    """

    def __init__(self, api_user=None, api_password=None, api_version="v2.1"):
        self.base_url = check_env.check("NEWMODE_API_URL", API_URL)
        self.api_user = check_env.check("NEWMODE_API_USER", api_user)
        self.api_password = check_env.check("NEWMODE_API_PASSWORD", api_password)
        self.api_version = check_env.check("NEWMODE_API_VERSION", api_version)
        self.headers = {"Content-Type": "application/json"}
        self.url = f"{self.base_url}{self.api_version}/"
        self.client = APIConnector(
            self.api_url_with_version,
            auth=(self.api_user, self.api_password),
            headers=self.headers,
        )

    def base_request(
        self,
        endpoint,
        method,
        requires_csrf=True,
        params={},
    ):

        url = endpoint

        if requires_csrf:
            csrf = self.get_csrf_token()
            self.headers["X-CSRF-Token"] = csrf

        response = None
        if method == "GET":
            response = self.client.get_request(url=url, params=params)
        elif method == "PATCH":
            response = self.client.patch_request(url=url, params=params)
        return response

    def get_csrf_token(self, max_attempts=10):
        """
        Retrieve a CSRF token for making API requests
        `Args:`
            max_attempts: int
                The maximum number of attempts to get the CSRF token.
        `Returns:`
            The CSRF token.
        """
        for attempt in range(max_attempts):
            try:
                response = self.base_request(
                    endpoint="session/token", method="GET", requires_csrf=False
                )
                return response
            except Exception as e:
                logger.warning(
                    f"Attempt {attempt} at getting CSRF Token failed. Retrying. Error: {e}"
                )
                time.sleep(attempt + 1)
        logger.warning(f"Error getting CSRF Token after {max_attempts} attempts")

    def get_tools(self, params={}):
        """
        Retrieve all tools
        `Args:`
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Response object from the API request containing tools data.
        """
        response = self.base_request(endpoint="tool", method="GET", params=params)
        return response

    def get_tool(self, tool_id, params={}):
        """
        Retrieve a specific tool by ID
        `Args:`
            tool_id: str
                The ID of the tool to retrieve.
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Response object from the API request containing the tool data.
        """
        response = self.base_request(
            endpoint=f"tool/{tool_id}", method="GET", params=params
        )
        return response

    def lookup_targets(self, tool_id, search=None, params={}):
        """
        Lookup targets for a given tool
        `Args:`
            tool_id: str
                The ID of the tool to lookup targets for.
            search: str
                The search criteria (optional).
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Response object from the API request containing target data.
        """
        endpoint = f"lookup/{tool_id}"
        if search:
            endpoint += f"/{search}"
        response = self.base_request(endpoint=endpoint, method="GET", params=params)
        return response

    def get_action(self, tool_id, params={}):
        """
        Get action information for a specific tool
        `Args:`
            tool_id: str
                The ID of the tool to get action information for.
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Response object from the API request containing action data.
        """
        response = self.base_request(
            endpoint=f"action/{tool_id}", method="GET", params=params
        )
        return response

    def run_action(self, tool_id, payload, params={}):
        """
        Run a specific action for a tool
        `Args:`
            tool_id: str
                The ID of the tool to run the action for.
            payload: dict
                The data to post to run the action.
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Response object from the API request containing posted outreach information.
        """
        response = self.base_request(
            endpoint=f"action/{tool_id}", method="PATCH", payload=payload, params=params
        )
        return response

    def get_target(self, target_id, params={}):
        """
        Retrieve a specific target by ID
        `Args:`
            target_id: str
                The ID of the target to retrieve.
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Response object from the API request containing target data.
        """
        response = self.base_request(
            endpoint=f"target/{target_id}", method="GET", params=params
        )
        return response

    def get_campaigns(self, params={}):
        """
        Retrieve all campaigns
        `Args:`
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Response object from the API request containing campaigns data.
        """
        response = self.base_request(endpoint="campaign", method="GET", params=params)
        return response

    def get_campaign(self, campaign_id, params={}):
        """
        Retrieve a specific campaign by ID
        `Args:`
            campaign_id: str
                The ID of the campaign to retrieve.
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Response object from the API request containing campaign data.
        """
        response = self.base_request(
            endpoint=f"campaign/{campaign_id}", method="GET", params=params
        )
        return response

    def get_organizations(self, params={}):
        """
        Retrieve all organizations
        `Args:`
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Response object from the API request containing organizations data.
        """
        response = self.base_request(
            endpoint="organization", method="GET", params=params
        )
        return response

    def get_organization(self, organization_id, params={}):
        """
        Retrieve a specific organization by ID
        `Args:`
            organization_id: str
                The ID of the organization to retrieve.
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Response object from the API request containing organization data.
        """
        response = self.base_request(
            endpoint=f"organization/{organization_id}", method="GET", params=params
        )
        return response

    def get_services(self, params={}):
        """
        Retrieve all services
        `Args:`
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Response object from the API request containing services data.
        """
        response = self.base_request(endpoint="service", method="GET", params=params)
        return response

    def get_service(self, service_id, params={}):
        """
        Retrieve a specific service by ID
        `Args:`
            service_id: str
                The ID of the service to retrieve.
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Response object from the API request containing service data.
        """
        response = self.base_request(
            endpoint=f"service/{service_id}", method="GET", params=params
        )
        return response

    def get_targets(self, params={}):
        """
        Retrieve all targets
        `Args:`
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Response object from the API request containing targets data.
        """
        response = self.base_request(endpoint="target", method="GET", params=params)
        return response

    def get_outreaches(self, tool_id, params={}):
        """
        Retrieve all outreaches for a specific tool
        `Args:`
            tool_id: str
                The ID of the tool to get outreaches for.
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Response object from the API request containing outreaches data.
        """
        params["nid"] = str(tool_id)
        response = self.base_request(
            endpoint="outreach", method="GET", requires_csrf=False, params=params
        )
        return response

    def get_outreach(self, outreach_id, params={}):
        """
        Retrieve a specific outreach by ID
        `Args:`
            outreach_id: str
                The ID of the outreach to retrieve.
            params: dict
                Query parameters to include in the request.
        `Returns:`
            Response object from the API request containing outreach data.
        """
        response = self.base_request(
            endpoint=f"outreach/{outreach_id}", method="GET", params=params
        )
        return response


# from parsons.utilities.api_connector import APIConnector
# from parsons.utilities import check_env
# from parsons.etl import Table
# import logging

# logger = logging.getLogger(__name__)

# API_URL = "https://engage.newmode.net/api/"

# ##########


# class NewMode(object):
#     """
#     Instantiate Class
#     `Args`:
#         api_user:
#             The username to use for the API requests. Not required if ``NEWMODE_API_URL``
#             env variable set.
#         api_password:
#             The password to use for the API requests. Not required if ``NEWMODE_API_PASSWORD``
#             env variable set.
#         api_version:
#             The api version to use. Defaults to v1.0
#     Returns:
#         NewMode Class
#     """

#     def __init__(self, api_user=None, api_password=None, api_version="v2.1"):
#         self.base_url = check_env.check("NEWMODE_API_URL", API_URL)
#         self.api_user = check_env.check("NEWMODE_API_USER", api_user)
#         self.api_password = check_env.check("NEWMODE_API_PASSWORD", api_password)
#         self.api_version = check_env.check("NEWMODE_API_VERSION", api_version)
#         self.headers = {"Content-Type": "application/json"}
#         self.url = f"{self.base_url}{self.api_version}/"
#         self.client = APIConnector(
#             self.api_url_with_version,
#             auth=(self.api_user, self.api_password),
#             headers=self.headers,
#         )

#     def base_request(
#         self,
#         endpoint,
#         requires_csrf=True,
#         params={},
#     ):

#         url = endpoint

#         if requires_csrf:
#             csrf = self.get_csrf_token()
#             self.headers["X-CSRF-Token"] = csrf      
#         return self.client.get_request(url=url, params=params)

#     def get_csrf_token(self, max_attempts=10):
#         for attempt in range(max_attempts):
#             try:
#                 response = self.base_request(endpoint="session/token", requires_csrf=False)
#                 return response
#             except Exception as e:
#                 logger.warning(f"Attempt {attempt} at getting CSRF Token failed. Retrying. Error: {e}")
#         logger.warning(f"Error getting CSRF Token after {max_attempts} attempts")

#     def get_tools(self, params={}):
#         response = self.baseRequest(endpoint="tool", params=params)
#         return response
#         # if response.status_code == 200:
#         #     return response["_embedded"]["hal:tool"]
#         # else:
#         #     logging.warning("Error getting tools")
#         #     logging.warning(f"Status code: {response.status_code}")

#     def getTool(self, tool_id, params={}):
#         response = self.baseRequest("tool/" + str(tool_id), params=params)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             logging.warning("Error getting tool")
#             logging.warning(f"Status code: {response.status_code}")

#     """
#     Lookup targets for a given tool
#     Args:
#         tool_id:
#             The tool to lookup targets.
#         search:
#             The search criteria. It could be:
#             - Empty: If empty, return custom targets associated to the tool.
#             - Postal code: Return targets matched by postal code.
#             - Lat/Long: Latitude and Longitude pair separated by '::'.
#               Ex. 45.451596::-73.59912099999997. It will return targets
#               matched for those coordinates.
#             - Search term: For your csv tools, this will return targets
#               matched by given valid search term.
#         params:
#             Query params for request.
#     Returns:
#         Targets information.
#     """

#     def lookupTargets(self, tool_id, search=None, params={}):
#         endpoint = "lookup/" + str(tool_id)
#         if search:
#             endpoint += "/" + search
#         response = self.baseRequest(endpoint, params=params)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             logging.warning("Error looking up for targets")
#             logging.warning(f"Status code: {response.status_code}")

#     """
#     Get action information.
#     Args:
#         tool_id:
#             The tool to retrieve.
#     Returns:
#         Action information including structure to run the action.
#     """

#     def getAction(self, tool_id, params={}):
#         response = self.baseRequest("action/" + str(tool_id), params=params)

#         if response.status_code == 200:
#             return response.json()
#         else:
#             logging.warning("Error getting action")
#             logging.warning(f"Status code: {response.status_code}")

#     """
#     Run specific action
#     Args:
#         tool_id:
#             The tool to run.
#         payload:
#             The data to post to run the action.
#             This data structure will depend on what has been
#             returned by getAction.
#     Returns:
#         Posted outreach information.
#     """

#     def runAction(self, tool_id, payload, params={}):
#         response = self.baseRequest(
#             "action/" + str(tool_id), "PATCH", json.dumps(payload), params=params
#         )
#         if response.status_code == 200:
#             return response.json()
#         else:
#             logging.warning("Error running action")
#             logging.warning(f"Status code: {response.status_code}")

#     def getTarget(self, target_id, params={}):
#         response = self.baseRequest("target/" + str(target_id), params=params)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             logging.warning("Error getting target")
#             logging.warning(f"Status code: {response.status_code}")

#     def getCampaigns(self, params={}):
#         response = self.baseRequest("campaign", params=params)
#         if response.status_code == 200:
#             return response.json()["_embedded"]["hal:campaign"]
#         else:
#             logging.warning("Error getting campaigns")
#             logging.warning(f"Status code: {response.status_code}")

#     def getCampaign(self, campaign_id, params={}):
#         response = self.baseRequest("campaign/" + str(campaign_id), params=params)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             logging.warning("Error getting campaign")
#             logging.warning(f"Status code: {response.status_code}")

#     def getOrganizations(self, params={}):
#         response = self.baseRequest("organization", params=params)
#         if response.status_code == 200:
#             return response.json()["data"]
#         else:
#             logging.warning("Error getting organizations")
#             logging.warning(f"Status code: {response.status_code}")

#     def getOrganization(self, organization_id, params={}):
#         response = self.baseRequest(
#             "organization/" + str(organization_id), params=params
#         )
#         if response.status_code == 200:
#             return response.json()["data"]
#         else:
#             logging.warning("Error getting organization")
#             logging.warning(f"Status code: {response.status_code}")

#     def getServices(self, params={}):
#         response = self.baseRequest("service", params=params)
#         if response.status_code == 200:
#             return response.json()["_embedded"]["hal:service"]
#         else:
#             logging.warning("Error getting services")
#             logging.warning(f"Status code: {response.status_code}")

#     def getService(self, service_id, params={}):
#         response = self.baseRequest("service/" + str(service_id), params=params)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             logging.warning("Error getting service")
#             logging.warning(f"Status code: {response.status_code}")

#     def getTargets(self, params={}):
#         response = self.baseRequest("target", params=params)
#         if response.status_code == 200:
#             return response.json()["_embedded"]["hal:target"]
#         else:
#             logging.warning("Error getting targets")
#             logging.warning(f"Status code: {response.status_code}")

#     def getOutreaches(self, tool_id, params={}):
#         params["nid"] = str(tool_id)
#         error_count = 0
#         while error_count < 10:
#             try:
#                 response = self.baseRequest(
#                     "outreach", requires_csrf=False, params=params
#                 )
#                 if response.status_code == 200:
#                     return response.json()["_embedded"]["hal:outreach"]
#                 elif response.status_code == 429:
#                     logging.warning(f"{response.status_code}: {response.text}")
#                     logging.warning(f"Pausing to avoid rate limiting...")
#                     time.sleep(20)
#                 else:
#                     logging.warning("Error getting outreaches")
#                     logging.warning(f"Status code: {response.status_code}")
#                     logging.warning(f"Status message: {response.text}")
#                     error_count += 1
#                     time.sleep(20)
#             except Exception as e:
#                 logging.warning(f"Exception: {e}")
#                 break

#     def getOutreach(self, outreach_id, params={}):
#         response = self.baseRequest("outreach/" + str(outreach_id), params=params)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             logging.warning("Error getting outreach")
#             logging.warning(f"Status code: {response.status_code}")

# # logger = logging.getLogger(__name__)

# # API_URL = "https://engage.newmode.net/api/"

# # class Newmode:
# #     def __init__(self, api_user=None, api_password=None, api_version=None):
# #         """
# #         Args:
# #             api_user: str
# #                 The Newmode api user. Not required if ``NEWMODE_API_USER`` env variable is
# #                 passed.
# #             api_password: str
# #                 The Newmode api password. Not required if ``NEWMODE_API_PASSWORD`` env variable is
# #                 passed.
# #             api_version: str
# #                 The Newmode api version. Defaults to "v1.0" or the value of ``NEWMODE_API_VERSION``
# #                 env variable.
# #         Returns:
# #             Newmode class
# #         """
# #         self.api_user = check_env.check("NEWMODE_API_USER", api_user)
# #         self.api_password = check_env.check("NEWMODE_API_PASSWORD", api_password)

# #         if api_version is None:
# #             api_version = "v1.0"

# #         self.api_version = check_env.check("NEWMODE_API_VERSION", api_version)

# #         self.client = Client(api_user, api_password, api_version)

# #     def convert_to_table(self, data):
# #         # Internal method to create a Parsons table from a data element.
# #         table = None
# #         if type(data) is list:
# #             table = Table(data)
# #         else:
# #             table = Table([data])

# #         return table

# #     def get_tools(self, params={}):
# #         """
# #         Get existing tools.
# #         Args:
# #             params:
# #                 Extra parameters sent to New/Mode library.
# #         Returns:
# #             Tools information as table.
# #         """
# #         tools = self.client.getTools(params=params)
# #         if tools:
# #             return self.convert_to_table(tools)
# #         else:
# #             logging.warning("Empty tools returned")
# #             return self.convert_to_table([])

# #     def get_tool(self, tool_id, params={}):
# #         """
# #         Get specific tool.
# #         Args:
# #             tool_id:
# #                 The id of the tool to return.
# #             params:
# #                 Extra parameters sent to New/Mode library.
# #         Returns:
# #             Tool information.
# #         """
# #         tool = self.client.getTool(tool_id, params=params)
# #         if tool:
# #             return tool
# #         else:
# #             logging.warning("Empty tool returned")
# #             return None

# #     def lookup_targets(self, tool_id, search=None, params={}):
# #         """
# #         Lookup targets for a given tool
# #         Args:
# #             tool_id:
# #                 The tool to lookup targets.
# #             search:
# #                 The search criteria. It could be:
# #                 - Empty: If empty, return custom targets associated to the tool.
# #                 - Postal code: Return targets matched by postal code.
# #                 - Lat/Long: Latitude and Longitude pair separated by '::'.
# #                 Ex. 45.451596::-73.59912099999997. It will return targets
# #                 matched for those coordinates.
# #                 - Search term: For your csv tools, this will return targets
# #                 matched by given valid search term.
# #         Returns:
# #             Targets information as table.
# #         """
# #         targets = self.client.lookupTargets(tool_id, search, params=params)
# #         if targets:
# #             data = []
# #             for key in targets:
# #                 if key != "_links":
# #                     data.append(targets[key])
# #             return self.convert_to_table(data)
# #         else:
# #             logging.warning("Empty targets returned")
# #             return self.convert_to_table([])

# #     def get_action(self, tool_id, params={}):
# #         """
# #         Get the action information for a given tool.
# #         Args:
# #             tool_id:
# #                 The id of the tool to return.
# #             params:
# #                 Extra parameters sent to New/Mode library.
# #         Returns:
# #             Tool action information.
# #         """
# #         action = self.client.getAction(tool_id, params=params)
# #         if action:
# #             return action
# #         else:
# #             logging.warning("Empty action returned")
# #             return None

# #     def run_action(self, tool_id, payload, params={}):
# #         """
# #         Run specific action with given payload.
# #         Args:
# #             tool_id:
# #                 The id of the tool to run.
# #             payload:
# #                 Payload data used to run the action. Structure will depend
# #                 on the stuff returned by get_action.
# #             params:
# #                 Extra parameters sent to New/Mode library.
# #         Returns:
# #             Action link (if otl) or sid.
# #         """
# #         action = self.client.runAction(tool_id, payload, params=params)
# #         if action:
# #             if "link" in action:
# #                 return action["link"]
# #             else:
# #                 return action["sid"]
# #         else:
# #             logging.warning("Error in response")
# #             return None

# #     def get_target(self, target_id, params={}):
# #         """
# #         Get specific target.
# #         Args:
# #             target_id:
# #                 The id of the target to return.
# #             params:
# #                 Extra parameters sent to New/Mode library.
# #         Returns:
# #             Target information.
# #         """
# #         target = self.client.getTarget(target_id, params=params)
# #         if target:
# #             return target
# #         else:
# #             logging.warning("Empty target returned")
# #             return None

# #     def get_targets(self, params={}):
# #         """
# #         Get all targets

# #         Args:
# #             params dict:
# #                 Extra paramaters sent to New/Mode library

# #         Returns:
# #             Target information
# #         """

# #         targets = self.client.getTargets(params=params)

# #         if targets:
# #             return self.convert_to_table(targets)

# #         else:
# #             logging.warning("No targets returned")
# #             return None

# #     def get_campaigns(self, params={}):
# #         """
# #         Get existing campaigns.
# #         Args:
# #             params:
# #                 Extra parameters sent to New/Mode library.
# #         Returns:
# #             Campaigns information as table.
# #         """
# #         campaigns = self.client.getCampaigns(params=params)
# #         if campaigns:
# #             return self.convert_to_table(campaigns)
# #         else:
# #             logging.warning("Empty campaigns returned")
# #             return self.convert_to_table([])

# #     def get_campaign(self, campaign_id, params={}):
# #         """
# #         Get specific campaign.
# #         Args:
# #             campaign_id:
# #                 The id of the campaign to return.
# #             params:
# #                 Extra parameters sent to New/Mode library.
# #         Returns:
# #             Campaign information.
# #         """
# #         campaign = self.client.getCampaign(campaign_id, params=params)
# #         if campaign:
# #             return campaign
# #         else:
# #             logging.warning("Empty campaign returned")
# #             return None

# #     def get_organizations(self, params={}):
# #         """
# #         Get existing organizations.
# #         Args:
# #             params:
# #                 Extra parameters sent to New/Mode library.
# #         Returns:
# #             Organizations information as table.
# #         """
# #         organizations = self.client.getOrganizations(params=params)
# #         if organizations:
# #             return self.convert_to_table(organizations)
# #         else:
# #             logging.warning("Empty organizations returned")
# #             return self.convert_to_table([])

# #     def get_organization(self, organization_id, params={}):
# #         """
# #         Get specific organization.
# #         Args:
# #             organization_id:
# #                 The id of the organization to return.
# #             params:
# #                 Extra parameters sent to New/Mode library.
# #         Returns:
# #             Organization information.
# #         """
# #         organization = self.client.getOrganization(organization_id, params=params)
# #         if organization:
# #             return organization
# #         else:
# #             logging.warning("Empty organization returned")
# #             return None

# #     def get_services(self, params={}):
# #         """
# #         Get existing services.
# #         Args:
# #             params:
# #                 Extra parameters sent to New/Mode library.
# #         Returns:
# #             Services information as table.
# #         """
# #         services = self.client.getServices(params=params)
# #         if services:
# #             return self.convert_to_table(services)
# #         else:
# #             logging.warning("Empty services returned")
# #             return self.convert_to_table([])

# #     def get_service(self, service_id, params={}):
# #         """
# #         Get specific service.
# #         Args:
# #             service_id:
# #                 The id of the service to return.
# #             params:
# #                 Extra parameters sent to New/Mode library.
# #         Returns:
# #             Service information.
# #         """
# #         service = self.client.getService(service_id, params=params)
# #         if service:
# #             return service
# #         else:
# #             logging.warning("Empty service returned")
# #             return None

# #     def get_outreaches(self, tool_id, params={}):
# #         """
# #         Get existing outreaches for a given tool.
# #         Args:
# #             tool_id:
# #                 Tool to return outreaches.
# #             params:
# #                 Extra parameters sent to New/Mode library.
# #         Returns:
# #             Outreaches information as table.
# #         """
# #         outreaches = self.client.getOutreaches(tool_id, params=params)
# #         if outreaches:
# #             return self.convert_to_table(outreaches)
# #         else:
# #             logging.warning("Empty outreaches returned")
# #             return self.convert_to_table([])

# #     def get_outreach(self, outreach_id, params={}):
# #         """
# #         Get specific outreach.
# #         Args:
# #             outreach_id:
# #                 The id of the outreach to return.
# #             params:
# #                 Extra parameters sent to New/Mode library.
# #         Returns:
# #             Outreach information.
# #         """
# #         outreach = self.client.getOutreach(outreach_id, params=params)
# #         if outreach:
# #             return outreach
# #         else:
# #             logging.warning("Empty outreach returned")
# #             return None
