import logging

from parsons.utilities.api_connector_next import APIConnector

logger = logging.getLogger(__name__)


class VanConnector(APIConnector):
    def items(self, endpoint, **kwargs):
        response = self.get_request(endpoint, **kwargs)

        data = response.json()
        next_page_url = data["nextPageLink"]
        items = data["items"]

        yield from items

        while items and isinstance(data, dict) and next_page_url:
            response = self.session.get(next_page_url, **kwargs)
            data = response.json()
            next_page_url = data["nextPageLink"]
            items = data["items"]

            yield from items

    @property
    def api_key_profile(self):
        """
        Returns the API key profile with includes permissions and other metadata.
        """

        return self.get("apiKeyProfiles")[0]

    @property
    def soap_client(self):
        from suds.client import Client

        if not self._soap_client:
            # Create the SOAP client
            soap_auth = {
                "Header": {
                    "DatabaseMode": self.soap_client_db(),
                    "APIKey": self.api_key,
                }
            }
            self._soap_client = Client(
                "https://api.securevan.com/Services/V3/ListService.asmx?WSDL", soapheaders=soap_auth
            )

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
