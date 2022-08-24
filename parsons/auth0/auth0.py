from parsons.etl.table import Table
from parsons.utilities import check_env
import requests


class Auth0(object):
    """
    Instantiate the Auth0 class

    `Args:`
        client_id: str
            The Auth0 client ID. Not required if ``AUTH0_CLIENT_ID`` env variable set.
        client_secret: str
            The Auth0 client secret. Not required if ``AUTH0_CLIENT_SECRET`` env variable set.
        domain: str
            The Auth0 domain. Not required if ``AUTH0_DOMAIN`` env variable set.
    `Returns:`
        Auth0 Class
    """
    def __init__(self, client_id=None, client_secret=None, domain=None):
        self.base_url = f"https://{check_env.check('AUTH0_DOMAIN', domain)}"
        access_token = requests.post(f'{self.base_url}/oauth/token', data={
            'grant_type': 'client_credentials',  # OAuth 2.0 flow to use
            'client_id': check_env.check('AUTH0_CLIENT_ID', client_id),
            'client_secret': check_env.check('AUTH0_CLIENT_SECRET', client_secret),
            'audience': f'{self.base_url}/api/v2/'
        }).json().get('access_token')
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

    def delete_user(self, id):
        """
        Delete Auth0 user.

        `Args:`
            id: str
                The user ID of the record to delete.
        `Returns:`
            int
        """
        return requests.delete(
            f'{self.base_url}/api/v2/users/{id}', headers=self.headers
        ).status_code

    def get_users_by_email(self, email):
        """
        Get Auth0 users by email.

        `Args:`
            email: str
                The user email of the record to get.
        `Returns:`
            Table Class
        """
        return Table(requests.get(
            f'{self.base_url}/api/v2/users-by-email', headers=self.headers, params={'email': email}
        ).json())
