import os
import json
import logging

from parsons.google.utitities import setup_google_application_credentials
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

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

        self.client = build("slides", "v1", credentials=credentials)

    def create_presentation(self, title):
        """
        `Args:`
            title: str
                this is the title you'd like to give your presentation
        `Returns:`
            the presentation object
        """

        body = {"title": title}
        presentation = self.client.presentations().create(body=body).execute()
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
            self.client.presentations().get(presentationId=presentation_id).execute()
        )

        return presentation

    def duplicate_slide(self, presentation_id, source_slide_number):
        """
        `Args:`
            presentation_id: str
                this is the ID of the presentation to put the duplicated slide
            source_slide_number: int
                this should reflect the slide # (e.g. 2 = 2nd slide)
        `Returns:`
            the duplicated slide object
        """
        source_slide = self.get_slide(presentation_id, source_slide_number)
        source_slide_id = source_slide["objectId"]

        batch_request = {
            "requests": [{"duplicateObject": {"objectId": source_slide_id}}]
        }
        response = (
            self.client.presentations()
            .batchUpdate(presentationId=presentation_id, body=batch_request)
            .execute()
        )

        duplicated_slide = response["replies"][0]["duplicateObject"]

        return duplicated_slide

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

        presentation = self.get_presentation(presentation_id)
        slide = presentation["slides"][slide_number - 1]

        return slide

    def delete_slide(self, presentation_id, slide_number):
        """
        `Args:`
            presentation_id: str
                this is the ID of the presentation to put the duplicated slide
            slide_number: int
                the slide number you are seeking
        `Returns:`
            None
        """
        slide_object_id = self.get_slide(presentation_id, slide_number)['objectId']
        
        requests = [
            {
                'deleteObject': {
                    'objectId': slide_object_id
                }
            }
        ]

        # Execute the request
        body = {
            'requests': requests
        }
        self.client.presentations().batchUpdate(
            presentationId=presentation_id,
            body=body
        ).execute()

        return None

    def replace_slide_text(
        self, presentation_id, slide_number, original_text, replace_text
    ):
        """
        `Args:`
            presentation_id: str
                this is the ID of the presentation to put the duplicated slide
            slide_number: int
                this should reflect the slide # (e.g. 2 = 2nd slide)
            origianl_text: str
                the text to be replaced
            replace_text: str
                the desired new text
        `Returns:`
            None
        """

        slide = self.get_slide(presentation_id, slide_number)
        slide_id = slide["objectId"]

        reqs = [
            {
                "replaceAllText": {
                    "containsText": {"text": original_text},
                    "replaceText": replace_text,
                    "pageObjectIds": [slide_id],
                }
            },
        ]

        self.client.presentations().batchUpdate(
            body={"requests": reqs}, presentationId=presentation_id
        ).execute()

        return None

    def get_slide_images(self, presentation_id, slide_number):
        """
        `Args:`
            presentation_id: str
                this is the ID of the presentation to put the duplicated slide
            slide_number: int
                this should reflect the slide # (e.g. 2 = 2nd slide)
        `Returns:`
            a list of object dicts for image objects
        """

        slide = self.get_slide(presentation_id, slide_number)

        images = []
        for x in slide["pageElements"]:
            if "image" in x.keys():
                images.append(x)

        return images

    def replace_slide_image(
        self, presentation_id, slide_number, image_obj, new_image_url
    ):
        """
        `Args:`
            presentation_id: str
                this is the ID of the presentation to put the duplicated slide
            slide_number: int
                this should reflect the slide # (e.g. 2 = 2nd slide)
            image_obj: dict
                the image object -- can use `get_slide_images()`
            new_image_url: str
                the url that contains the desired image
        `Returns:`
            None
        """

        slide = self.get_slide(presentation_id, slide_number)

        reqs = [
            {
                "createImage": {
                    "url": new_image_url,
                    "elementProperties": {
                        "pageObjectId": slide["objectId"],
                        "size": image_obj["size"],
                        "transform": image_obj["transform"],
                    },
                }
            },
            {"deleteObject": {"objectId": image_obj["objectId"]}},
        ]

        self.client.presentations().batchUpdate(
            body={"requests": reqs}, presentationId=presentation_id
        ).execute()

        return None
