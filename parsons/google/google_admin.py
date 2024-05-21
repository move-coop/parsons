import uuid

from google.auth.transport.requests import AuthorizedSession

from parsons.etl.table import Table
from parsons.google.utilities import (
    load_google_application_credentials,
    setup_google_application_credentials,
)


class GoogleAdmin(object):
    """
    A connector for Google Admin.


    `Args:`
        app_creds: str
            A credentials json string or a path to a json file. Not required if
            ``GOOGLE_APPLICATION_CREDENTIALS`` env variable set.
        sub: str
            An email address that this service account will act on behalf of (via domain-wide
            delegation)
    `Returns:`
        GoogleAdmin Class
    """

    def __init__(self, app_creds=None, sub=None):
        env_credentials_path = str(uuid.uuid4())
        setup_google_application_credentials(app_creds, target_env_var_name=env_credentials_path)
        credentials = load_google_application_credentials(
            env_credentials_path,
            scopes=["https://www.googleapis.com/auth/admin.directory.group"],
            subject=sub,
        )

        self.client = AuthorizedSession(credentials)

    def _paginate_request(self, endpoint, collection, params=None):
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

    def get_aliases(self, group_key, params=None):
        """
        Get aliases for a group. `Google Admin API Documentation <https://developers.google.com/\
        admin-sdk/directory/reference/rest/v1/groups.aliases/list>`_

        `Args:`
            group_key: str
                The Google group id
            params: dict
                A dictionary of fields for the GET request
        `Returns:`
            Table Class
        """
        return self._paginate_request("groups/" + group_key + "/aliases", "aliases", params)

    def get_all_group_members(self, group_key, params=None):
        """
        Get all members in a group. `Google Admin API Documentation <https://developers.google.com/\
        admin-sdk/directory/v1/guides/manage-group-members#get_all_members>`_

        `Args:`
            group_key: str
                The Google group id
            params: dict
                A dictionary of fields for the GET request
        `Returns:`
            Table Class
        """
        return self._paginate_request("groups/" + group_key + "/members", "members", params)

    def get_all_groups(self, params=None):
        """
        Get all groups in a domain or account. `Google Admin API Documentation <https://developers.\
        google.com/admin-sdk/directory/v1/guides/manage-groups#get_all_domain_groups>`_
        `Args:`
            params: dict
                A dictionary of fields for the GET request.
        `Returns:`
            Table Class
        """
        return self._paginate_request("groups", "groups", params)
