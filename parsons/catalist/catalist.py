"""Utilities for working with the Catalist Match API

Install dependencies with `pip install parsons[catalist]`
"""

import base64
import logging
import os
import tempfile
import time
import urllib
from typing import Optional, Union, Dict, List
from zipfile import ZipFile

from parsons.etl import Table
from parsons.sftp import SFTP
from parsons.utilities.oauth_api_connector import OAuth2APIConnector

logger = logging.getLogger(__name__)


class CatalistMatch:
    """Connector for working with the Catalist Match API.

    This API allows a trusted third party to submit new files for processing, and/or
    reprocess existing files. It also allows retrieval of processing status. Initial
    setup of template(s) via the M Tool UI will be required.

    The Catalist Match tool requires OAuth2.0 client credentials for the API as well as
    credentials for accessing the Catalist sftp bucket. Each Catalist client is given
    their own bucket alias named after a tree species, used for constructing the
    filepath within the sftp bucket.

    Accessing the Catalist sftp bucket and Match API both require the source IP address
    to be explicitly white-listed by Catalist.

    Example usage:
    ```
    tbl = Table.from_csv(...)
    client = CatalistMatch(...)
    match_result = client.match(tbl)
    ```

    Note that matching can take from 10 minutes up to 6 hours or longer to complete, so
    you may want to think strategically about how to await completion without straining
    your compute resources on idling.

    To separate submitting the job and fetching the result:
    ```
    tbl = Table.from_csv(...)
    client = CatalistMatch(...)
    response = client.upload(tbl)
    match_result = client.await_completion(response["id"])
    ```

    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        sftp_username: str,
        sftp_password: str,
        client_audience: Optional[str] = None,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.connection = OAuth2APIConnector(
            "https://api.catalist.us/mapi/",
            client_id=client_id,
            client_secret=client_secret,
            authorization_kwargs={"audience": client_audience or "catalist_api_m_prod"},
            token_url="https://auth.catalist.us/oauth/token",
            auto_refresh_url="https://auth.catalist.us/oauth/token",
        )
        self.sftp = SFTP("t.catalist.us", sftp_username, sftp_password)

    def load_table_to_sftp(self, table: Table, input_subfolder: Optional[str] = None) -> str:
        """Load table to Catalist sftp bucket as gzipped CSV for matching.

        If input_subfolder is specific, the file will be uploaded to a subfolder of the
        myUploads directory in the SFTP server.

        `Args:`
             table: Table
                 Parsons Table for matching. "first_name" and "last_name" columns
                 are required. Optional columns for matching: last_name, name_suffix,
                 addr1, addr2, city, state, zip, phone, email, gender_tomatch, dob,
                 dob_year, matchbackid.
             input_subfolder: str
                 Optional. If specified, the file will be uploaded to a subfolder of the
                 myUploads directory in the SFTP server.
        """
        local_path = table.to_csv(temp_file_compression="gzip")
        hashed_name = hash(time.time())
        remote_path_parts = ["myUploads", f"{hashed_name}.csv.gz"]
        if input_subfolder:
            if input_subfolder not in self.sftp.list_directory("/myUploads/"):
                self.sftp.make_directory("/myUploads/" + input_subfolder)
            remote_path_parts.insert(1, input_subfolder)
        remote_path = "/".join(remote_path_parts)

        self.sftp.put_file(local_path, remote_path)

        # Loads to Catalist SFTP bucket are expcted in the client's uploads bucket
        # So we don't need to explicitly include that part of the path
        result = f"file://{remote_path.replace('myUploads/', '')}"
        return result

    def match(
        self,
        table: Table,
        export: bool = False,
        description: Optional[str] = None,
        export_filename_suffix: Optional[str] = None,
        input_subfolder: Optional[str] = None,
        copy_to_sandbox: bool = False,
        static_values: Optional[Dict[str, Union[str, int]]] = None,
    ) -> Table:
        """Load table to the Catalist Match API, returns matched table.

         This method blocks until the match completes, which can take from 10 minutes to
         6 hours or more depending on concurrent traffic.

        `Args:`
             table: Table
                 Parsons Table for matching. "first_name" and "last_name" columns
                 are required. Optional columns for matching: last_name, name_suffix,
                 addr1, addr2, city, state, zip, phone, email, gender_tomatch, dob,
                 dob_year, matchbackid.
             export: bool
                 Defaults to False
             description: str
                 Optional. Description for the match job.
             export_filename_suffix: str
                 Optional. Adds a suffix to the result filename in the SFTP server.
             input_subfolder: str
                 Optional. Adds a prefix to the filepath of the uploaded input file in
                 the SFTP server.
             copy_to_sandbox: bool
                  Defaults to False.
             static_values: dict
                  Optional. Any included values are mapped to every row of the input table.
        """
        response = self.upload(
            table=table,
            export=export,
            description=description,
            export_filename_suffix=export_filename_suffix,
            input_subfolder=input_subfolder,
            copy_to_sandbox=copy_to_sandbox,
            static_values=static_values,
        )
        result = self.await_completion(response["id"])
        return result

    def upload(
        self,
        table: Table,
        template_id: str = "48827",
        export: bool = False,
        description: Optional[str] = None,
        export_filename_suffix: Optional[str] = None,
        input_subfolder: Optional[str] = None,
        copy_to_sandbox: bool = False,
        static_values: Optional[Dict[str, Union[str, int]]] = None,
    ) -> dict:
        """Load table to the Catalist Match API, returns response with job metadata.

        `Args:`
             table: Table
                 Parsons Table for matching. "first_name" and "last_name" columns
                 are required. Optional columns for matching: last_name, name_suffix,
                 addr1, addr2, city, state, zip, phone, email, gender_tomatch, dob,
                 dob_year, matchbackid.
             template_id: str
                 Defaults to 48827, currently the only available template for working
                 with the Match API.
             export: bool
                 Defaults to False
             description: str
                 Optional. Description for the match job.
             export_filename_suffix: str
                 Optional. Adds a suffix to the result filename in the SFTP server.
             input_subfolder: str
                 Optional. Adds a prefix to the filepath of the uploaded input file in
                 the SFTP server.
             copy_to_sandbox: bool
                  Defaults to False.
             static_values: dict
                  Optional. Any included values are mapped to every row of the input table.
        """

        self.validate_table(table, template_id)

        # upload table to s3 temp location
        sftp_file_path = self.load_table_to_sftp(table, input_subfolder)
        sftp_file_path_encoded = base64.b64encode(sftp_file_path.encode("ascii")).decode("ascii")

        if export:
            action = "export%2Cpublish"
        else:
            action = "publish"

        # Create endpoint using options
        endpoint_params = [
            "upload",
            "template",
            template_id,
            "action",
            action,
            "url",
            sftp_file_path_encoded,
        ]

        if description:
            endpoint_params.extend(["description", description])

        endpoint = "/".join(endpoint_params)

        # Assemble query parameters
        query_params: Dict[str, Union[str, int]] = {"token": self.connection.token["access_token"]}
        if copy_to_sandbox:
            query_params["copyToSandbox"] = "true"
        if static_values:
            query_params.update(static_values)
        if export_filename_suffix:
            query_params["subClientName"] = export_filename_suffix

        logger.debug(f"Executing request to endpoint {self.connection.uri + endpoint}")

        endpoint = endpoint + "?" + urllib.parse.urlencode(query_params)

        response = self.connection.get_request(endpoint)

        result = response[0]

        return result

    def action(
        self,
        file_ids: Union[str, List[str]],
        match: bool = False,
        export: bool = False,
        export_filename_suffix: Optional[str] = None,
        copy_to_sandbox: bool = False,
    ) -> List[dict]:
        """Perform actions on existing files.

        All files must be in Finished status (if the action requested is publish), and
        must mapped against the same template. The request will return as soon as the
        action has been queued.

        `Args:`
             file_ids: str or List[str]
                 one or more file_ids (found in the `id` key of responses from the
                 upload() or status() methods)
             match: bool
                 Optional. Defaults to False. If True, will initiate matching.
             export: bool
                 Optional. Defaults to False. If True, will initiate export.
             export_filename_suffix: str
                 Optional. If included, adds a suffix to the filepath of the exported
                 file in the SFTP server.
             copy_to_sandbox: bool
                  Defaults to False.

        """
        actions = ["publish"]
        if match:
            actions.append("match")
        if export:
            actions.append("export")
        action = urllib.parse.quote(",".join(actions))

        endpoint_params = ["action", action]

        if isinstance(file_ids, list):
            encoded_files = urllib.parse.quote(",".join(file_ids))
        else:
            encoded_files = file_ids

        endpoint_params.extend(["file", encoded_files])

        endpoint = "/".join(endpoint_params)

        logger.debug(f"Executing request to endpoint {self.connection.uri + endpoint}")

        query_params = {"token": self.connection.token["access_token"]}
        if copy_to_sandbox:
            query_params["copyToSandbox"] = "true"
        if export_filename_suffix:
            query_params["subClientName"] = export_filename_suffix

        endpoint = endpoint + "?" + urllib.parse.urlencode(query_params)

        result = self.connection.get_request(endpoint)

        return result

    def status(self, id: str) -> dict:
        """Check status of a match job."""
        endpoint = "/".join(["status", "id", id])
        query_params = {"token": self.connection.token["access_token"]}
        result = self.connection.get_request(endpoint, params=query_params)
        return result

    def await_completion(self, id: str, wait: int = 30) -> Table:
        """Await completion of a match job. Return matches when ready.

        This method will poll the status of a match job on a timer until the job is
        complete. By default, polls once every 30 seconds.

        Note that match job completion can take from 10 minutes up to 6 hours or more
        depending on concurrent traffic. Consider your strategy for polling for
        completion."""
        while True:
            response = self.status(id)
            status = response["process"]["processState"]
            if status in ("Finished", "Error", "Stopped", "Exception"):
                logger.info(f"Job {id} is complete with status {status}.")
                break

            logger.info(f"Job {id} has status {status}, awaiting completion.")
            time.sleep(wait)

        result = self.load_matches(id)
        return result

    def load_matches(self, id: str) -> Table:
        """Take a completed job ID, download and open the match file as a Table.

        Result will be a Table with all the original columns along with columns 'DWID',
        'CONFIDENCE', 'ZIP9', and 'STATE'. The original column headers will be prepended
        with 'COL#-'."""
        # Validate that the job is complete
        response = self.status(str(id))
        status = response["process"]["processState"]

        if status == "Finished":
            logger.info(f"Validated that job {id} completed successfully.")
        else:
            err_msg = "Failed to successfully run match job. "
            if status == "Error":
                err_msg += "Internal error. "
            elif status == "Stopped":
                err_msg += "Probably stopped by Catalist staff. Will be rerun. "
            elif status == "Exception":
                err_msg += (
                    "Error with data. Catalist will have been notified and "
                    "will contact you or rerun the file. "
                )
            else:
                "Unknown or unexpected final status."
            err_msg += f"[job={id}, final_status={status}]"
            raise RuntimeError(err_msg)

        remote_filepaths = self.sftp.list_directory("/myDownloads/")
        remote_filename = [filename for filename in remote_filepaths if id in filename][0]
        remote_filepath = "/myDownloads/" + remote_filename
        temp_file_zip = self.sftp.get_file(remote_filepath)
        temp_dir = tempfile.mkdtemp()

        with ZipFile(temp_file_zip) as zf:
            zf.extractall(path=temp_dir)

        filepath = os.listdir(temp_dir)[0]

        result = Table.from_csv(os.path.join(temp_dir, filepath), delimiter="\t")
        return result

    def validate_table(self, table: Table, template_id: str = "48827") -> None:
        """Validate table structure and contents."""
        if not template_id == "48827":
            logger.warn(f"No validator implemented for template {template_id}.")
            return

        expected_table_columns = [
            "first_name",
            "middle_name",
            "last_name",
            "name_suffix",
            "addr1",
            "addr2",
            "city",
            "state",
            "zip",
            "phone",
            "email",
            "gender_tomatch",
            "dob",
            "dob_year",
            "matchbackid",
        ]

        required_columns: List[str] = ["first_name", "last_name"]
        actual_table_columns = table.columns

        unexpected_columns = [
            col for col in actual_table_columns if col not in expected_table_columns
        ]
        missing_required_columns = [
            col for col in required_columns if col not in actual_table_columns
        ]

        errors = {}
        if unexpected_columns:
            errors["unexpected_columns"] = unexpected_columns
        if missing_required_columns:
            errors["missing_required_columns"] = missing_required_columns

        if errors:
            raise ValueError("Input table does not have the right structure. %s", errors)
        else:
            logger.info("Table structure validated.")
