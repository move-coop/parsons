import json

import requests
from parsons.etl.table import Table
from parsons.utilities import check_env


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
        access_token = (
            requests.post(
                f"{self.base_url}/oauth/token",
                data={
                    "grant_type": "client_credentials",  # OAuth 2.0 flow to use
                    "client_id": check_env.check("AUTH0_CLIENT_ID", client_id),
                    "client_secret": check_env.check(
                        "AUTH0_CLIENT_SECRET", client_secret
                    ),
                    "audience": f"{self.base_url}/api/v2/",
                },
            )
            .json()
            .get("access_token")
        )
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
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
            f"{self.base_url}/api/v2/users/{id}", headers=self.headers
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
        url = f"{self.base_url}/api/v2/users-by-email"
        val = requests.get(url, headers=self.headers, params={"email": email})
        if val.status_code == 429:
            raise requests.exceptions.ConnectionError(val.json()["message"])
        return Table(val.json())

    def upsert_user(
        self,
        email,
        username=None,
        given_name=None,
        family_name=None,
        app_metadata={},
        user_metadata={},
    ):
        """
        Upsert Auth0 users by email.

        `Args:`
            email: str
                The user email of the record to get.
            username: optional str
                Username to set for user
            given_name: optional str
                Given to set for user
            family_name: optional str
                Family name to set for user
            app_metadata: optional dict
                App metadata to set for user
            user_metadata: optional dict
                User metadata to set for user
        `Returns:`
            Requests Response object
        """
        payload = json.dumps(
            {
                "email": email.lower(),
                "given_name": given_name,
                "family_name": family_name,
                "username": username,
                "connection": "Username-Password-Authentication",
                "app_metadata": app_metadata,
                "blocked": False,
                "user_metadata": user_metadata,
            }
        )
        existing = self.get_users_by_email(email.lower())
        if existing.num_rows > 0:
            a0id = existing[0]["user_id"]
            ret = requests.patch(
                f"{self.base_url}/api/v2/users/{a0id}",
                headers=self.headers,
                data=payload,
            )
        else:
            ret = requests.post(
                f"{self.base_url}/api/v2/users", headers=self.headers, data=payload
            )
        if ret.status_code != 200:
            raise ValueError(f"Invalid response {ret.json()}")
        return ret
