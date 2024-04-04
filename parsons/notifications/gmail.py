import base64
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from parsons.notifications.sendmail import SendMail

SCOPES = "https://www.googleapis.com/auth/gmail.send"


class Gmail(SendMail):
    """Create a Gmail object, for sending emails.

    `Args:`
        creds_path: str
            The path to the credentials.json file.
        token_path: str
            The path to the token.json file.
        user_id: str
            Optional; Sender email address. Defaults to the special value
            "me" which is used to indicate the authenticated user.
    """

    def __init__(self, creds_path=None, token_path=None, user_id="me"):

        self.user_id = user_id

        if not creds_path:
            raise ValueError("Invalid path to credentials.json.")

        if not token_path:
            raise ValueError("Invalid path to token.json.")

        self.store = file.Storage(token_path)
        self.creds = self.store.get()

        # BUG-1
        # http = httplib2shim.Http()

        if not self.creds or self.creds.invalid:
            flow = client.flow_from_clientsecrets(creds_path, SCOPES)
            self.creds = tools.run_flow(flow, self.store)

            # BUG-1
            # self.creds = self.run_flow(flow, self.store, http=http)

        self.service = build("gmail", "v1", http=self.creds.authorize(Http()))

        # BUG-1
        # self.service = build('gmail', 'v1', http=self.creds.authorize(http))

    def _encode_raw_message(self, message):
        return {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}

    def _send_message(self, msg):
        """Send an email message.

        `Args:`
            message: dict
                Message to be sent as a base64url encode object.
                i.e. the objects created by the create_* instance methods
        `Returns:`
            dict
                A Users.messages object see `https://developers.google.com/gmail/api/v1/reference/users/messages#resource.` # noqa
                for more info.
        """
        self.log.info("Sending a message...")

        message = self._encode_raw_message(msg)

        self.log.debug(message)

        try:
            message = (
                self.service.users().messages().send(userId=self.user_id, body=message).execute()
            )
        except HttpError:
            self.log.exception("An error occurred: while attempting to send a message.")
            raise
        else:
            self.log.debug(message)
            self.log.info(f"Message sent succesfully (Message Id: {message['id']})")

            return message
