import os
import json
import logging

from parsons.etl.table import Table
from parsons.google.utitities import setup_google_application_credentials
from parsons.tools.credential_tools import decode_credential
from google.oauth2 import service_account
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

class GoogleSlides:
    """
    A connector for Google Slides, handling slide creation.

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

        scope = [
            "https://www.googleapis.com/auth/presentations",
            "https://www.googleapis.com/auth/drive",
        ]

        setup_google_application_credentials(
            google_keyfile_dict, "GOOGLE_DRIVE_CREDENTIALS"
        )
        google_credential_file = open(os.environ["GOOGLE_DRIVE_CREDENTIALS"])
        credentials_dict = json.load(google_credential_file)

        credentials = Credentials.from_service_account_info(
            credentials_dict, scopes=scope, subject=subject
        )

        self.gsheets_client = build('slides', 'v1', credentials=credentials)

    
    def create_presentation(self, title):
        """
        `Args:`
            title: str
                this is the title you'd like to give your presentation
        `Returns:`
            the presentation object
        """

        body = {"title": title}
        presentation = self.presentations().create(body=body).execute()
        logger.info(
            f"Created presentation with ID:" f"{(presentation.get('presentationId'))}"
        )
        return presentation


    def get_presentation(self, presentation_id):
        """
        `Args:`
            presentation_id: str
                this is the ID of the presentation to put the duplicated slide
        `Returns:`
            the presentation object
        """

        presentation = (
            self.presentations().get(presentationId=presentation_id).execute()
        )

        return presentation


    def get_slide(self, presentation_id, slide_number):
        """
        `Args:`
            presentation_id: str
                this is the ID of the presentation to put the duplicated slide
            slide_number: int
                the slide number you are seeking
        `Returns:`
            the slide object
        """

        presentation = self.get_presentation(self, presentation_id)
        slide = presentation["slides"][slide_number - 1]

        return slide


    def duplicate_slide(self, source_slide_id, presentation_id):
        """
        `Args:`
            source_slide_id: str
                this is the ID of the source slide to be duplicated
            presentation_id: str
                this is the ID of the presentation to put the duplicated slide
        `Returns:`
            the ID of the duplicated slide
        """

        batch_request = {"requests": [{"duplicateObject": {"objectId": source_slide_id}}]}
        response = (
            self.presentations()
            .batchUpdate(presentationId=presentation_id, body=batch_request)
            .execute()
        )

        duplicated_slide_id = response["replies"][0]["duplicateObject"]["objectId"]

        return duplicated_slide_id


    def replace_slide_text(
        self, presentation_id, slide_id, original_text, replace_text
    ):
        """
        `Args:`
            presentation_id: str
                this is the ID of the presentation to put the duplicated slide
            origianl_text: str
                the text to be replaced
            replace_text: str
                the desired new text
        `Returns:`
            None
        """

        reqs = [
            {
                "replaceAllText": {
                    "containsText": {"text": original_text},
                    "replaceText": replace_text,
                    "pageObjectIds": [slide_id],
                }
            },
        ]s

        self.presentations().batchUpdate(
            body={"requests": reqs}, presentationId=presentation_id
        ).execute()

        return None


    def replace_slide_image(self, presentation_id, slide, obj, img_url):
        """
        `Args:`
            presentation_id: str
                this is the ID of the presentation to put the duplicated slide
            slide: dict
                the slide object
            replace_text: str
                the desired new text
        `Returns:`
            None
        """

        reqs = [
            {
                "createImage": {
                    "url": img_url,
                    "elementProperties": {
                        "pageObjectId": slide["objectId"],
                        "size": obj["size"],
                        "transform": obj["transform"],
                    },
                }
            },
            {"deleteObject": {"objectId": obj["objectId"]}},
        ]

        self.presentations().batchUpdate(
            body={"requests": reqs}, presentationId=presentation_id
        ).execute()

        return None