import gzip
import json
import logging
import time

import requests
from parsons.etl.table import Table
from parsons.utilities import check_env

logger = logging.getLogger(__name__)


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
                    "client_secret": check_env.check("AUTH0_CLIENT_SECRET", client_secret),
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
        connection="Username-Password-Authentication",
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
            ret = requests.patch(
                f"{self.base_url}/api/v2/users/{a0id}",
                headers=self.headers,
                data=payload,
            )
        else:
            ret = requests.post(f"{self.base_url}/api/v2/users", headers=self.headers, data=payload)
        if ret.status_code != 200:
            raise ValueError(f"Invalid response {ret.json()}")
        return ret

    def block_user(self, user_id, connection="Username-Password-Authentication"):
        """
        Blocks Auth0 users by email - setting the "blocked" attribute on Auth0's API.

        `Args:`
            user_id: str
                Auth0 user id
            connection: optional str
                Name of auth0 connection (default to Username-Password-Authentication)
        `Returns:`
            Requests Response object
        """
        payload = json.dumps({"connection": connection, "blocked": True})
        ret = requests.patch(
            f"{self.base_url}/api/v2/users/{user_id}",
            headers=self.headers,
            data=payload,
        )
        if ret.status_code != 200:
            raise ValueError(f"Invalid response {ret.json()}")
        return ret

    def retrieve_all_users(self, connection="Username-Password-Authentication"):
        """
        Retrieves all Auth0 users using the batch jobs endpoint.

        `Args:`
            connection: optional str
                Name of auth0 connection (default to Username-Password-Authentication)
        `Returns:`
            Requests Response object
        """
        connection_id = self.get_connection_id(connection)
        url = f"{self.base_url}/api/v2/jobs/users-exports"

        headers = self.headers

        fields = [
            {"name": n} for n in ["user_id", "username", "email", "user_metadata", "app_metadata"]
        ]
        # Start the users-export job
        response = requests.post(
            url,
            headers=headers,
            json={"connection_id": connection_id, "format": "json", "fields": fields},
        )
        job_id = response.json().get("id")

        if job_id:
            # Check job status until complete
            while True:
                status_response = requests.get(
                    f"{self.base_url}/api/v2/jobs/{job_id}", headers=headers
                )
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

    def get_connection_id(self, connection_name):
        """
        Retrieves an Auth0 connection_id corresponding to a specific connection name

        `Args:`
            connection_name: str
                Name of auth0 connection
        `Returns:`
            Connection ID string
        """
        url = f"{self.base_url}/api/v2/connections"

        response = requests.get(url, headers=self.headers)
        connections = response.json()

        for connection in connections:
            if connection["name"] == connection_name:
                return connection["id"]

        return None
