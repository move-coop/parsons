import gzip
import json
import logging
import time
from datetime import datetime, timedelta, timezone

import requests

from parsons.etl.table import Table
from parsons.utilities import check_env
from parsons.utilities.bearer_auth import BearerAuth

logger = logging.getLogger(__name__)


class Auth0:
    """Parsons connector for interacting with Auth0 endpoints."""

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        domain: str | None = None,
    ) -> None:
        """
        Instantiate the Auth0 class.

        Args:
            client_id:
                The Auth0 client ID.
                Not required if ``AUTH0_CLIENT_ID`` env variable set.
            client_secret:
                The Auth0 client secret.
                Not required if ``AUTH0_CLIENT_SECRET`` env variable set.
            domain:
                The Auth0 domain.
                Not required if ``AUTH0_DOMAIN`` env variable set.

        """
        self.base_url = f"https://{check_env.check('AUTH0_DOMAIN', domain)}"
        self.client_id = check_env.check("AUTH0_CLIENT_ID", client_id)
        self.client_secret = check_env.check("AUTH0_CLIENT_SECRET", client_secret)
        self.headers = {"Content-Type": "application/json"}
        self._refresh_access_token()

    def _refresh_access_token(self) -> tuple[str, datetime]:
        url = f"{self.base_url}/oauth/token"
        payload = {
            "grant_type": "client_credentials",  # OAuth 2.0 flow to use
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "audience": f"{self.base_url}/api/v2/",
        }
        token_res = requests.post(url, data=payload).json()
        access_token = token_res.get("access_token")
        token_type = token_res.get("token_type")
        expires_in = token_res.get("expires_in")

        expiration = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        self.auth = BearerAuth(
            access_token,
            token_name=token_type,
            expires=expiration,
            refresh_callback=self._refresh_access_token,
        )
        return access_token, expiration

    def delete_user(self, id: str) -> int:
        """
        Delete Auth0 user.

        Args:
            id: The user ID of the record to delete.

        """
        url = f"{self.base_url}/api/v2/users/{id}"
        return requests.delete(url, headers=self.headers, auth=self.auth).status_code

    def get_users_by_email(self, email: str) -> Table:
        """
        Get Auth0 users by email.

        Args:
            email: The user email of the record to get.

        """
        url = f"{self.base_url}/api/v2/users-by-email"
        val = requests.get(url, headers=self.headers, auth=self.auth, params={"email": email})
        if val.status_code == 429:
            raise requests.exceptions.ConnectionError(val.json()["message"])
        return Table(val.json())

    def upsert_user(
        self,
        email: str,
        username: str | None = None,
        given_name: str | None = None,
        family_name: str | None = None,
        app_metadata: dict | None = None,
        user_metadata: dict | None = None,
        connection: str = "Username-Password-Authentication",
    ) -> requests.Response:
        """
        Upsert Auth0 users by email.

        Args:
            email: The user email of the record to get.
            username: Username to set for user
            given_name: Given to set for user
            family_name: Family name to set for user
            app_metadata: App metadata to set for user
            user_metadata: User metadata to set for user
            connection: Name of auth0 connection. Defaults to ``Username-Password-Authentication``.

        """
        if user_metadata is None:
            user_metadata = {}
        if app_metadata is None:
            app_metadata = {}
        obj = {
            "email": email.lower(),
            "username": username,
            "connection": connection,
            "app_metadata": app_metadata,
            "blocked": False,
            "user_metadata": user_metadata,
        }
        if given_name is not None:
            obj["given_name"] = given_name
        if family_name is not None:
            obj["family_name"] = family_name
        payload = json.dumps(obj)

        existing = self.get_users_by_email(email.lower())
        if existing.num_rows > 0:
            a0id = existing[0]["user_id"]
            url = f"{self.base_url}/api/v2/users/{a0id}"
            ret = requests.patch(url, headers=self.headers, auth=self.auth, data=payload)
        else:
            url = f"{self.base_url}/api/v2/users"
            ret = requests.post(url, headers=self.headers, auth=self.auth, data=payload)
        if ret.status_code != 200:
            raise ValueError(f"Invalid response {ret.json()}")
        return ret

    def block_user(
        self, user_id: str, connection: str = "Username-Password-Authentication"
    ) -> requests.Response:
        """
        Block Auth0 users by email - setting the "blocked" attribute on Auth0's API.

        Args:
            user_id: Auth0 user id
            connection: Name of auth0 connection. Defaults to ``Username-Password-Authentication``.

        """
        url = f"{self.base_url}/api/v2/users/{user_id}"
        payload = json.dumps({"connection": connection, "blocked": True})
        ret = requests.patch(url, headers=self.headers, auth=self.auth, data=payload)
        if ret.status_code != 200:
            raise ValueError(f"Invalid response {ret.json()}")
        return ret

    def retrieve_all_users(
        self, connection: str = "Username-Password-Authentication"
    ) -> Table | None:
        """
        Retrieve all Auth0 users using the batch jobs endpoint.

        Args:
            connection: Name of auth0 connection. Defaults to ``Username-Password-Authentication``.

        """
        connection_id = self.get_connection_id(connection)
        url = f"{self.base_url}/api/v2/jobs/users-exports"
        fields = [
            {"name": n} for n in ["user_id", "username", "email", "user_metadata", "app_metadata"]
        ]
        payload = {"connection_id": connection_id, "format": "json", "fields": fields}
        # Start the users-export job
        response = requests.post(url, headers=self.headers, auth=self.auth, json=payload)
        job_id = response.json().get("id")

        if job_id:
            # Check job status until complete
            while True:
                url = f"{self.base_url}/api/v2/jobs/{job_id}"
                status_response = requests.get(url, headers=self.headers, auth=self.auth)
                status_data = status_response.json()
                if status_response.status_code == 429:
                    time.sleep(10)

                elif status_response.status_code != 200:
                    break
                elif status_data.get("status") == "completed":
                    download_url = status_data.get("location")
                    break
                elif status_data.get("status") == "failed":
                    logger.error("Retrieve members job failed to complete.")
                    return None

            # Download the users-export file
            users_response = requests.get(download_url)

            decompressed_data = gzip.decompress(users_response.content).decode("utf-8")
            users_data = []
            for d in decompressed_data.split("\n"):
                if d:
                    users_data.append(json.loads(d))

            return Table(users_data)

        logger.error("Retrieve members job creation failed")
        return None

    def get_connection_id(self, connection_name: str) -> str | None:
        """
        Retrieve an Auth0 connection_id corresponding to a specific connection name.

        Args:
            connection_name: Name of auth0 connection

        Returns:
            Connection ID

        """
        url = f"{self.base_url}/api/v2/connections"
        response = requests.get(url, headers=self.headers, auth=self.auth)
        connections = response.json()

        for connection in connections:
            if connection["name"] == connection_name:
                return connection["id"]

        return None
