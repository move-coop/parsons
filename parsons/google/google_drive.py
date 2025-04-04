import logging
import os
import tempfile
import uuid
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

    def create_folder(self, name: str, parents: list[str] | str | None = None) -> str:
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

    def find_subfolder(self, subfolder_name: str, parent_folder_id: str) -> str | None:
        response = (
            self.client.files()
            .list(
                q=f"'{parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder'",
                fields="files(id, name)",
            )
            .execute()
        )
        match = [i for i in response.get("files") if i.get("name") == subfolder_name]
        if match:
            result = match[0].get("id")
        else:
            result = None
        return result

    def find_file_in_folder(
        self, file_name: str, folder_id: str, fields: list[str] | None = None
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
        self, folder_id: str, fields: list[str] | None = None
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

        with open(filepath, "wb") as file:
            downloader = MediaIoBaseDownload(file, self.client.files().get_media(fileId=file_id))
            while not done:
                status, done = downloader.next_chunk()
        return filepath

    def upload_file(self, file_path: str, parent_folder_id: str) -> str:
        file_metadata = {
            "name": os.path.basename(file_path),
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
        file_name = os.path.basename(file_path)
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
