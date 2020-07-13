import os

import adal


class AzureAccountAccess(object):
    """
    Instantiate AzureAccountAccess Class for a given Azure storage account.
    This class is not yet fully built out, and will later have an __init__
    function added.

    `Returns:`
        `AzureAccountAccess`
    """

    def get_refresh_azure_token(self, client_id, client_secret):
        RESOURCE = "https://storage.azure.com/"
        authority_url = os.environ('AUTHORITY_URL')
        context = adal.AuthenticationContext(authority_url)
        token = context.acquire_token_with_client_credentials(RESOURCE, client_id, client_secret)

        return token
