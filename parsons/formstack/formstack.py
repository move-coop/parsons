import logging
from typing import Optional

from parsons import Table
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector

logger = logging.getLogger(__name__)

API_URI = "https://www.formstack.com/api/v2"


class Formstack(object):
    """
    Instantiate Formstack class.

       `Args:`
            api_token:
                API token to access the Formstack API. Not required if the
                ``FORMSTACK_API_TOKEN`` env variable is set.
    """

    def __init__(self, api_token: Optional[str] = None):
        self.api_token = check_env.check("FORMSTACK_API_TOKEN", api_token)
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_token}",
        }
        self.client = APIConnector(API_URI, headers=headers)

    def _get_paginated_request(
        self, url: str, data_key: str, params: dict = {}, large_request: bool = False
    ) -> Table:
        """
        Make a GET request for any endpoint that returns a list of data. Will check pagination.

        This is suitable for endpoints like `GET /form`, which gets all forms. It is not suitable
        for endpoints like `GET /form/:id`, which returns the data for one particular form,
        and is never paginated.

        Author's note: I have observed some inconsistency in how Formstack is paginating its
            its endpoints. For example, the /form endpoint (mentioned above) is documented as
            if it follows Formstack's standard pagination scheme. However, it seems to just
            return all of your form data and does not include the pagination keys at all.
            So for developing this connector, I'm just experimenting with endpoints as I write
            the methods for them and using `_get_paginated_request` as needed. Fortunately using
            the connector will remove the need to worry about this from the caller, and we can
            udated the methods in this class as needed when/if Formstack changes pagination on
            their API.

        `Args:`
            url: string
                Relative URL (from the Formstack base URL) to make the request.

            data_key: string
                JSON key that will hold the data in the response body.

            params: Dictionary, optional
                Params to pass to the request.

            large_request: Boolean, optional
                If the response is likely to include a large number of pages. Defaults to `False`.
                In rare cases the API will return more pages than `parsons.Table` is able to handle.
                Pass `True` to enable a workaround for these endpoints.

        `Returns:`
            Table Class
                A table with the returned data.
        """
        data = Table()
        page = 1
        pages = None

        while pages is None or page <= pages:
            req_params = {**params, "page": page}
            response_data = self.client.get_request(url, req_params)
            pages = response_data["pages"]
            data.concat(Table(response_data[data_key]))

            if large_request:
                data.materialize()

            page += 1

        return data

    def get_folders(self) -> Table:
        """
        Get all folders on your account and their subfolders.

        `Returns:`
            Table Class
                A Table with the folders data.
        """
        response_data = self.client.get_request("folder")
        logger.debug(response_data)

        # The API returns folders in a tree structure that doesn't fit well
        # into a Table. Fortunately, subfolders can't themselves have subfolders.
        subfolders = []
        for f in response_data["folders"]:
            f_subfolders = f.get("subfolders")
            if f_subfolders is not None:
                subfolders += f_subfolders

        tbl = Table(response_data["folders"] + subfolders)
        logger.debug(f"Found {tbl.num_rows} folders.")

        if tbl.num_rows == 0:
            return Table()

        tbl.convert_column("id", int)
        tbl.convert_column("parent", lambda p: None if p == "0" else int(p))
        tbl.remove_column("subfolders")
        return tbl

    def get_forms(self, form_name: Optional[str] = None, folder_id: Optional[int] = None) -> Table:
        """
        Get all forms on your account.

        `Args:`
            form_name: string, optional
                Search by form name.
            folder_id: int, optional
                Return forms in the specified folder.

        `Returns:`
            Table Class
                A table with the forms data.
        """
        params = {}
        if form_name:
            params["search"] = form_name
        if folder_id:
            params["folder"] = folder_id
        response_data = self.client.get_request("form", params)
        logger.debug(response_data)
        return Table(response_data["forms"])

    def get_submission(self, id: int) -> dict:
        """
        Get the details of the specified submission.

        `Args:`
            id: int
                ID for the submission to retrieve.

        `Returns:`
            Dictionary
                Submission data.
        """
        response_data = self.client.get_request(f"submission/{id}")
        logger.debug(response_data)
        return response_data

    def get_form_submissions(self, form_id: int, **query_params) -> Table:
        """
        Get all submissions for the specified form.

        Note this only returns the meta-data about the submissions, not the answer data,
        by default. To get the responses pass `data=True` as a query param.

        For more useful options, such as how to filter the responses by date,
        check the Formstack documentation.

        `Args:`
            form_id: int
                The form ID for the form of the submissions.
            query_params: kwargs
                Query arguments to pass to the form/submissions endpoint.

        `Returns:`
            Table Class
                A Table with the submission data for the form.
        """
        tbl = self._get_paginated_request(
            f"form/{form_id}/submission", "submissions", query_params, True
        )
        logger.debug(tbl)
        return tbl

    def get_form_fields(self, form_id: int) -> Table:
        """
        Get all fields for the specified form.

        `Args:`
            form_id: int
                The form ID for the form of the submissions.

        `Returns:`
            Table Class
                A Table with the fields on the form.
        """
        response_data = self.client.get_request(f"form/{form_id}/field")
        logger.debug(response_data)
        tbl = Table(response_data)
        return tbl
