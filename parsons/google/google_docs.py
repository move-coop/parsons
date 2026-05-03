import logging
import uuid
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build

from parsons.google.utilities import (
    load_google_application_credentials,
    setup_google_application_credentials,
)

logger = logging.getLogger(__name__)


class GoogleDocs:
    """
    A connector for Google Docs

    Args:
        app_creds:
            Can be a dictionary of Google Drive API credentials, parsed from JSON provided
            by the Google Developer Console, or a path string pointing to credentials
            saved on disk, or a :class:`google.oauth2.service_account.Credentials` object.
            Required if env variable ``GOOGLE_DRIVE_CREDENTIALS`` is not populated.

    """

    def __init__(
        self,
        app_creds: service_account.Credentials | str | Path | dict | None = None,
    ):
        scopes = [
            "https://www.googleapis.com/auth/documents",
            "https://www.googleapis.com/auth/drive",
        ]

        if isinstance(app_creds, service_account.Credentials):
            credentials = app_creds
        else:
            env_credentials_path = str(uuid.uuid4())
            setup_google_application_credentials(
                app_creds, target_env_var_name=env_credentials_path
            )
            credentials = load_google_application_credentials(env_credentials_path, scopes=scopes)

        self.client = build(
            "docs",
            "v1",
            credentials=credentials,
            cache_discovery=False,
        )
