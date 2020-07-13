import adal

class AzureAccountAccess(object):
    def get_refresh_azure_token(self, client_id, client_secret):
        RESOURCE = "https://storage.azure.com/"
        authority_url = "https://login.microsoftonline.com/openprogress.com"
        context = adal.AuthenticationContext(authority_url)
        token = context.acquire_token_with_client_credentials(RESOURCE, client_id, client_secret)

        return token