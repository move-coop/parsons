# Adapted from Gmail API tutorial https://developers.google.com/gmail/api
from apiclient import errors
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email.encoders import encode_base64
from email.utils import parseaddr
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from validate_email import validate_email
import base64
import logging
import mimetypes
import os

# BUG: can't send files equal to or larger than 6MB
# There is a possible fix
# `BUG-1` are the changes that would need to be made

# BUG-1
# import httplib2shim
# import sys

logger = logging.getLogger(__name__)

SCOPES = 'https://www.googleapis.com/auth/gmail.send'


class Gmail(object):
    """Create a Gmail object, for sending emails.

    `Args:`
        creds_path: str
            The path to the credentials.json file.
        token_path: str
            The path to the token.json file.
    """

    def __init__(self, creds_path=None, token_path=None):

        self.user_id = 'me'

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

        self.service = build('gmail', 'v1', http=self.creds.authorize(Http()))

        # BUG-1
        # self.service = build('gmail', 'v1', http=self.creds.authorize(http))

    def create_message_simple(self, sender, to, subject, message_text):
        """Create a text-only message for an email.

        `Args:`
            sender: str
                Email address of the sender.
            to: str
                Email address(es) of the recipient(s).
            subject: str
                The subject of the email message.
            message_text: str
                The text of the email message.
        `Returns:`
            dict
                An object containing a base64url encoded email object.
        """
        logger.info("Creating a simple message...")

        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject

        msg = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

        logger.debug(msg)
        logger.info("Encoded simple message sucessfully created.")

        return msg

    def create_message_html(self, sender, to, subject, message_text,
                            message_html):
        """Create an html message for an email.

        `Args:`
            sender: str
                Email address of the sender.
            to: str
                Email address(es) of the recipient(s).
            subject: str
                The subject of the email message.
            message_text: str
                The text of the email message.
            message_html: str
                The html formatted text of the email message.
        `Returns:`
            dict
                An object containing a base64url encoded email object.
        """
        logger.info("Creating an html message...")

        message = MIMEMultipart('alternative')
        message['subject'] = subject
        message['from'] = sender
        message['to'] = to
        if message_text:
            message.attach(MIMEText(message_text, 'plain'))
        message.attach(MIMEText(message_html, 'html'))

        msg = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

        logger.debug(msg)
        logger.info("Encoded html message sucessfully created.")

        return msg

    def create_message_attachments(self, sender, to, subject, message_text,
                                   files, message_html=None):
        """Create a message for an email that includes an attachment.

        `Args:`
            sender: str
                Email address of the sender.
            to: str
                Email address of the receiver.
            subject: str
                The subject of the email message.
            message_text: str
                The text of the email message.
            files: list
                The path(s) to the file(s) to be attached.
            message_html: str
                Optional; The html formatted text of the email message.
        `Returns:`
            dict
                An object containing a base64url encoded email object.
        """
        logger.info("Creating a message with attachments...")

        message = MIMEMultipart('alternative')
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject

        msg = MIMEText(message_text, 'plain')
        message.attach(msg)

        if message_html:
            html = MIMEText(message_html, 'html')
            message.attach(html)

        for f in files:
            content_type, encoding = mimetypes.guess_type(f)
            logger.debug(
                f"(File: {f}, Content-type: {content_type}, "
                f"Encoding: {encoding})")

            if content_type is None or encoding is not None:
                content_type = 'application/octet-stream'

            main_type, sub_type = content_type.split('/', 1)

            if main_type == 'text':
                logger.info("Added a text file.")
                fp = open(f, 'rb')
                msg = MIMEText(fp.read(), _subtype=sub_type, _charset='utf-8')
                fp.close()

            elif main_type == 'image':
                logger.info("Added an image file.")
                fp = open(f, 'rb')
                msg = MIMEImage(fp.read(), _subtype=sub_type)
                filename = os.path.basename(f)
                msg.add_header('Content-ID', f'<{filename}>')
                fp.close()

            elif main_type == 'audio':
                logger.info("Added an audio file.")
                fp = open(f, 'rb')
                msg = MIMEAudio(fp.read(), _subtype=sub_type)
                fp.close()

            elif main_type == 'application':
                logger.info("Added an application file.")
                fp = open(f, 'rb')
                msg = MIMEApplication(fp.read(), _subtype=sub_type)
                fp.close()

            else:
                logger.info("Added an unknown-type file.")
                fp = open(f, 'rb')
                msg = MIMEBase(main_type, sub_type)
                msg.set_payload(fp.read())
                encode_base64(msg)
                fp.close()

            filename = os.path.basename(f)
            msg.add_header(
                'Content-Disposition', 'attachment', filename=filename)
            message.attach(msg)

        m = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

        logger.debug(m)
        logger.info("Encoded message with attachments sucessfully created.")

        return m

    def _validate_email_string(self, str):
        logger.debug(f"Validating email {str}...")
        realname, email_addr = parseaddr(str)

        if not email_addr:
            raise ValueError("Invalid email address.")

        if not validate_email(email_addr):
            raise ValueError("Invalid email address.")

        return True

    def send_message(self, message, user_id=None):
        """Send an email message.

        `Args:`
            message: dict
                Message to be sent as a base64url encode object.
            user_id: str
                Optional; User's email address. Defaults to the special value
                "me" which is used to indicate the authenticated user.
        `Returns:`
            dict
                A Users.messages object see `https://developers.google.com/gmail/api/v1/reference/users/messages#resource.` # noqa
                for more info.
        """
        logger.info("Sending a message...")
        if not user_id:
            user_id = self.user_id
        try:
            message = (self.service.users().messages()
                       .send(userId=user_id, body=message).execute())
        except errors.HttpError:
            logger.exception(
                'An error occurred: while attempting to send a message.')
            raise
        else:
            logger.debug(message)
            logger.info(
                f"Message sent succesfully (Message Id: {message['id']})")

            return message

    def send_email(self, sender, to, subject, message_text, message_html=None,
                   files=None):
        """Send an email message.

        `Args:`
            sender: str
                Email address of the sender.
            to: str or list
                Email address(es) of the receiver(s). Must be in correct email
                string syntax. For example, `name@email.com` or
                `"Name" <email@email.com>`.
            subject: str
                The subject of the email message.
            message_text: str
                The text of the email message.
            message_html: str
                The html formatted text of the email message. If ommitted, the
                email is sent a text-only body.
            files: str or list
                The path to the file(s) to be attached.

        `Returns:`
            An object containing a base64url encoded email object.
        """
        logger.info("Preparing to send and email...")

        logger.info("Validating email(s)")
        if isinstance(to, list):
            if len(to) == 0:
                raise EmptyListError("Must contain at least 1 email.")

            for e in to:
                self._validate_email_string(e)

            to = ', '.join(to)

        elif isinstance(to, str):
            self._validate_email_string(to)

        if not message_html and not files:
            msg_type = 'simple'
            msg = self.create_message_simple(sender, to, subject, message_text)

        elif not files:
            msg_type = 'html'
            msg = self.create_message_html(
                sender, to, subject, message_text, message_html)
        else:
            msg_type = 'attachments'
            if isinstance(files, str):
                files = [files]

            msg = self.create_message_attachments(
                sender, to, subject, message_text, files, message_html)

        logger.info(f"Sending a(n) {msg_type} email...")

        self.send_message(msg)

        logger.info("Email sent succesfully.")


class EmptyListError(IndexError):
    """Throw when a list is empty that should contain at least 1 element."""
    pass
