from suds.client import Client
import logging
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector

logger = logging.getLogger(__name__)

URI = "https://api.securevan.com/v4/"
SOAP_URI = "https://api.securevan.com/Services/V3/ListService.asmx?WSDL"


class VANConnector(object):
    def __init__(self, api_key=None, auth_name="default", db=None):

        self.api_key = check_env.check("VAN_API_KEY", api_key)

        if db == "MyVoters":
            self.db_code = 0
        elif db in ["MyMembers", "MyCampaign", "EveryAction"]:
            self.db_code = 1
        else:
            raise KeyError(
                "Invalid database type specified. Pick one of:"
                " MyVoters, MyCampaign, MyMembers, EveryAction."
            )

        self.uri = URI
        self.db = db
        self.auth_name = auth_name
        self.pagination_key = "nextPageLink"
        self.auth = (self.auth_name, self.api_key + "|" + str(self.db_code))
        self.api = APIConnector(
            self.uri,
            auth=self.auth,
            data_key="items",
            pagination_key=self.pagination_key,
        )

        # We will not create the SOAP client unless we need to as this triggers checking for
        # valid credentials. As not all API keys are provisioned for SOAP, this keeps it from
        # raising a permission exception when creating the class.
        self._soap_client = None

    @property
    def api_key_profile(self):
        """
        Returns the API key profile with includes permissions and other metadata.
        """

        return self.get_request("apiKeyProfiles")[0]

    @property
    def soap_client(self):

        if not self._soap_client:

            # Create the SOAP client
            soap_auth = {
                "Header": {
                    "DatabaseMode": self.soap_client_db(),
                    "APIKey": self.api_key,
                }
            }
            self._soap_client = Client(SOAP_URI, soapheaders=soap_auth)

        return self._soap_client

    def soap_client_db(self):
        """
        Parse the REST database name to the accepted SOAP format
        """

        if self.db == "MyVoters":
            return "MyVoterFile"
        if self.db == "EveryAction":
            return "MyCampaign"
        else:
            return self.db

    def get_request(self, endpoint, **kwargs):

        r = self.api.get_request(self.uri + endpoint, **kwargs)
        data = self.api.data_parse(r)

        # Paginate
        while isinstance(r, dict) and self.api.next_page_check_url(r):
            if endpoint == "savedLists" and not r["items"]:
                break
            if endpoint == "printedLists" and not r["items"]:
                break
            r = self.api.get_request(r[self.pagination_key], **kwargs)
            data.extend(self.api.data_parse(r))
        return data

    def post_request(self, endpoint, **kwargs):

        return self.api.post_request(endpoint, **kwargs)

    def delete_request(self, endpoint, **kwargs):

        return self.api.delete_request(endpoint, **kwargs)

    def patch_request(self, endpoint, **kwargs):

        return self.api.patch_request(endpoint, **kwargs)

    def put_request(self, endpoint, **kwargs):

        return self.api.put_request(endpoint, **kwargs)
