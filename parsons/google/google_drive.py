import os
import json
import logging

from parsons.google.utitities import setup_google_application_credentials
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)


class GoogleDrive:
    """
    A connector for Google Drive, largely handling permissions.

    `Args:`
        google_keyfile_dict: dict
            A dictionary of Google Drive API credentials, parsed from JSON provided
            by the Google Developer Console. Required if env variable
            ``GOOGLE_DRIVE_CREDENTIALS`` is not populated.
        subject: string
            In order to use account impersonation, pass in the email address of the account to be
            impersonated as a string.
    """

    def __init__(self, google_keyfile_dict=None, subject=None):

        scope = ["https://www.googleapis.com/auth/drive"]

        setup_google_application_credentials(
            google_keyfile_dict, "GOOGLE_DRIVE_CREDENTIALS"
        )
        google_credential_file = open(os.environ["GOOGLE_DRIVE_CREDENTIALS"])
        credentials_dict = json.load(google_credential_file)

        credentials = Credentials.from_service_account_info(
            credentials_dict, scopes=scope, subject=subject
        )

        self.client = build("drive", "v3", credentials=credentials)

    def get_permissions(self, file_id):
        """
        `Args:`
            file_id: str
                this is the ID of the object you are hoping to share
        `Returns:`
            permission dict
        """

        p = self.client.permissions().list(fileId=file_id).execute()

        return p

    def _share_object(self, file_id, permission_dict):

        # Send the request to share the file
        p = (
            self.client.permissions()
            .create(fileId=file_id, body=permission_dict)
            .execute()
        )

        return p

    def share_object(self, file_id, email_addresses=None, role="reader", type="user"):
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
                {"type": type, "role": role, "domain": email}
                for email in email_addresses
            ]
        else:
            permissions = [
                {"type": type, "role": role, "emailAddress": email}
                for email in email_addresses
            ]

        new_permissions = []
        for permission in permissions:
            p = self._share_object(file_id, permission)
            new_permissions.append(p)

        return new_permissions

    def transfer_ownership(self, file_id, new_owner_email):
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

        return None
