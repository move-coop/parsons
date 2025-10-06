import logging
import tempfile
import uuid
from pathlib import Path
from typing import Optional, Union

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from parsons.google.utilities import (
    load_google_application_credentials,
    setup_google_application_credentials,
)

logger = logging.getLogger(__name__)


class GoogleDrive:
    """
    A connector for Google Drive

    `Args:`
        app_creds: dict | str | Credentials
            Can be a dictionary of Google Drive API credentials, parsed from JSON provided
            by the Google Developer Console, or a path string pointing to credentials
            saved on disk, or a google.oauth2.credentials.Credentials object. Required
            if env variable ``GOOGLE_DRIVE_CREDENTIALS`` is not populated.
    """

    def __init__(
        self,
        app_creds: Optional[Union[str, dict, Credentials]] = None,
    ):
        scopes = [
            "https://www.googleapis.com/auth/drive",
        ]

        if isinstance(app_creds, Credentials):
            credentials = app_creds
        else:
            env_credentials_path = str(uuid.uuid4())
            setup_google_application_credentials(
                app_creds, target_env_var_name=env_credentials_path
            )
            credentials = load_google_application_credentials(env_credentials_path, scopes=scopes)

        self.client = build(
            "drive",
            "v3",
            credentials=credentials,
            cache_discovery=False,
        )

    def create_folder(self, name: str, parents: Union[list[str], str, None] = None) -> str:
        if isinstance(parents, str):
            parents = [parents]
        elif parents is None:
            parents = []
        response = (
            self.client.files()
            .create(
                body={
                    "name": name,
                    "mimeType": "application/vnd.google-apps.folder",
                    "parents": parents,
                },
                fields="id",
            )
            .execute()
        )
        return response.get("id")

    def find_subfolder(self, subfolder_name: str, parent_folder_id: str) -> Optional[str]:
        response = (
            self.client.files()
            .list(
                q=f"'{parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder'",
                fields="files(id, name)",
            )
            .execute()
        )
        match = [i for i in response.get("files") if i.get("name") == subfolder_name]
        result = match[0].get("id") if match else None
        return result

    def find_file_in_folder(
        self, file_name: str, folder_id: str, fields: Optional[list[str]] = None
    ) -> list[dict[str, str]]:
        if not fields:
            fields = ["id", "name"]
        page_token = None
        results = []
        while True:
            response = (
                self.client.files()
                .list(
                    q=f"'{folder_id}' in parents and name = '{file_name}'",
                    spaces="drive",
                    fields="nextPageToken, files({})".format(",".join(fields)),
                    pageToken=page_token,
                )
                .execute()
            )
            results.extend(response.get("files", []))
            page_token = response.get("nextPageToken")
            if page_token is None:
                break
        return results

    def list_files_in_folder(
        self, folder_id: str, fields: Optional[list[str]] = None
    ) -> list[dict[str, str]]:
        if not fields:
            fields = ["id", "name"]
        page_token = None
        results = []
        while True:
            response = (
                self.client.files()
                .list(
                    q=f"'{folder_id}' in parents",
                    spaces="drive",
                    fields="nextPageToken, files({})".format(",".join(fields)),
                    pageToken=page_token,
                    supportsTeamDrives=True,
                    includeItemsFromAllDrives=True,
                )
                .execute()
            )
            results.extend(response.get("files", []))
            page_token = response.get("nextPageToken")
            if page_token is None:
                break
        return results

    def empty_folder(self, folder_id: str) -> None:
        folder_contents = self.list_files_in_folder(folder_id)
        for drive_file in folder_contents:
            self.client.files().delete(
                fileId=drive_file.get("id"),
            ).execute()

    def download_file(self, file_id: str) -> str:
        """Download file from Drive to disk. Returns local filepath."""
        filepath = tempfile.mkstemp()[1]
        done = False

        with Path(filepath).open(mode="wb") as file:
            downloader = MediaIoBaseDownload(file, self.client.files().get_media(fileId=file_id))
            while not done:
                status, done = downloader.next_chunk()
        return filepath

    def upload_file(self, file_path: str, parent_folder_id: str) -> str:
        file_metadata = {
            "name": Path(file_path).name,
            "parents": [parent_folder_id],
        }
        media = MediaFileUpload(file_path)
        response = (
            self.client.files().create(body=file_metadata, media_body=media, fields="id").execute()
        )
        return response.get("id")

    def replace_file(self, file_path: str, file_id: str) -> str:
        """Replace file in drive."""
        media = MediaFileUpload(file_path)
        resp = self.client.files().update(fileId=file_id, media_body=media, fields="id").execute()
        return resp.get("id")

    def upsert_file(self, file_path: str, parent_folder_id: str) -> str:
        """Create or replace file in drive folder, based on file name."""
        file_name = Path(file_path).name
        match_response = (
            self.client.files()
            .list(
                q=f"name='{file_name}' and '{parent_folder_id}' in parents",
                spaces="drive",
                fields="files(id, name)",
            )
            .execute()
            .get("files", [])
        )
        if match_response:
            file_id = match_response[0].get("id")
            result = self.replace_file(file_path, file_id)
        else:
            result = self.upload_file(file_path, parent_folder_id)
        return result

    def get_permissions(self, file_id: str) -> dict:
        """
        `Args:`
            file_id: str
                this is the ID of the object you are hoping to share
        `Returns:`
            permission dict
        """

        p = self.client.permissions().list(fileId=file_id).execute()

        return p

    def _share_object(self, file_id: str, permission_dict: dict) -> dict:
        # Send the request to share the file
        p = self.client.permissions().create(fileId=file_id, body=permission_dict).execute()

        return p

    def share_object(
        self,
        file_id: str,
        email_addresses: Optional[list[str]] = None,
        role: str = "reader",
        type: str = "user",
    ) -> list[dict]:
        """
        `Args:`
            file_id: str
                this is the ID of the object you are hoping to share
            email_addresses: list
                this is the list of the email addresses you want to share;
                set to a list of domains like `['domain']` if you choose `type='domain'`;
                set to `None` if you choose `type='anyone'`
            role: str
                Options are -- owner, organizer, fileOrganizer, writer, commenter, reader
                https://developers.google.com/drive/api/guides/ref-roles
            type: str
                Options are -- user, group, domain, anyone
        `Returns:`
            List of permission objects
        """
        if role not in [
            "owner",
            "organizer",
            "fileOrganizer",
            "writer",
            "commenter",
            "reader",
        ]:
            raise Exception(
                f"{role} not from the allowed list of: \
                                owner, organizer, fileOrganizer, writer, commenter, reader"
            )

        if type not in ["user", "group", "domain", "anyone"]:
            raise Exception(
                f"{type} not from the allowed list of: \
                                user, group, domain, anyone"
            )

        if type == "domain":
            permissions = [
                {"type": type, "role": role, "domain": email} for email in email_addresses
            ]
        else:
            permissions = [
                {"type": type, "role": role, "emailAddress": email} for email in email_addresses
            ]

        new_permissions = []
        for permission in permissions:
            p = self._share_object(file_id, permission)
            new_permissions.append(p)

        return new_permissions

    def transfer_ownership(self, file_id: str, new_owner_email: str) -> None:
        """
        `Args:`
            file_id: str
                this is the ID of the object you are hoping to share
            new_owner_email: str
                the email address of the intended new owner
        `Returns:`
            None
        """
        permissions = self.client.permissions().list(fileId=file_id).execute()

        # Find the current owner
        current_owner_permission = next(
            (p for p in permissions.get("permissions", []) if "owner" in p), None
        )

        if current_owner_permission:
            # Update the permission to transfer ownership
            new_owner_permission = {
                "type": "user",
                "role": "owner",
                "emailAddress": new_owner_email,
            }
            self.client.permissions().update(
                fileId=file_id,
                permissionId=current_owner_permission["id"],
                body=new_owner_permission,
            ).execute()
            logger.info(f"Ownership transferred successfully to {new_owner_email}.")
        else:
            logger.info("File does not have a current owner.")
