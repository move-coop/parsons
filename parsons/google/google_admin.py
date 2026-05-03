import uuid
from pathlib import Path

from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

from parsons import Table
from parsons.google.utilities import (
    load_google_application_credentials,
    setup_google_application_credentials,
)


class GoogleAdmin:
    """
    A connector for Google Admin.

    Args:
        app_creds:
            A credentials json string or a path to a json file.
            Not required if ``GOOGLE_APPLICATION_CREDENTIALS`` env variable is set.
        sub:
            An email address that this service account will act on behalf of
            (via domain-wide delegation).

    """

    def __init__(
        self,
        app_creds: service_account.Credentials | str | Path | dict | None = None,
        sub: str | None = None,
    ) -> None:
        if isinstance(app_creds, service_account.Credentials):
            credentials = app_creds
        else:
            env_credentials_path = str(uuid.uuid4())
            setup_google_application_credentials(
                app_creds, target_env_var_name=env_credentials_path
            )
            credentials = load_google_application_credentials(
                env_credentials_path,
                scopes=["https://www.googleapis.com/auth/admin.directory.group"],
                subject=sub,
            )

        self.client = AuthorizedSession(credentials)

    def _paginate_request(
        self, endpoint: str, collection: str, params: dict[str, str] | None = None
    ) -> Table:
        # Build query params
        param_arr = []
        param_str = ""
        if params:
            for key, value in params.items():
                param_arr.append(key + "=" + value)
            param_str = "?" + "&".join(param_arr)

        # Make API call
        req_url = "https://admin.googleapis.com/admin/directory/v1/" + endpoint

        # Return type from Google Admin is a tuple of length 2. Extract desired result from 2nd item
        # in tuple and convert to json
        res = self.client.request("GET", req_url + param_str).json()
        if "error" in res:
            raise RuntimeError(res["error"].get("message"))

        # Paginate
        ret = []
        if collection in res:
            ret = res[collection]

            while "nextPageToken" in res:
                if param_arr[-1][0:10] != "pageToken=":
                    param_arr.append("pageToken=" + res["nextPageToken"])
                else:
                    param_arr[-1] = "pageToken=" + res["nextPageToken"]
                response = self.client.request("GET", req_url + "?" + "&".join(param_arr)).json()
                if "error" in response:
                    raise RuntimeError(response["error"].get("message"))
                ret += response[collection]

        return Table(ret)

    def get_aliases(self, group_key: str, params: dict[str, str] | None = None) -> Table:
        """
        Get aliases for a group.

        `Google Admin API Documentation -- groups.aliases/list
        <https://developers.google.com/workspace/admin/directory/reference/rest/v1/groups.aliases/list>`__

        Args:
            group_key: The Google group id
            params: A dictionary of fields for the GET request

        """
        return self._paginate_request("groups/" + group_key + "/aliases", "aliases", params)

    def get_all_group_members(self, group_key: str, params: dict[str, str] | None = None) -> Table:
        """
        Get all members in a group.

        `Google Admin API Documentation -- manage-group-members#get_all_members
        <https://developers.google.com/workspace/admin/directory/v1/guides/manage-group-members#get_all_members>`__

        Args:
            group_key: The Google group id
            params: A dictionary of fields for the GET request

        """
        return self._paginate_request("groups/" + group_key + "/members", "members", params)

    def get_all_groups(self, params: dict[str, str] | None = None) -> Table:
        """
        Get all groups in a domain or account.

        `Google Admin API Documentation -- manage-groups#get_all_domain_groups
        <https://developers.google.com/workspace/admin/directory/v1/guides/manage-groups#get_all_domain_groups>`__

        Args:
            params: A dictionary of fields for the GET request.

        """
        return self._paginate_request("groups", "groups", params)
