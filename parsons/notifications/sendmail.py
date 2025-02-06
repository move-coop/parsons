# Adapted from Gmail API tutorial https://developers.google.com/gmail/api
from abc import ABC, abstractmethod
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email.encoders import encode_base64
from email.utils import parseaddr
from validate_email import validate_email
import io
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


class SendMail(ABC):
    """SendMail base class for sending emails.

    This class is not designed to be used directly,
    as it has useful methods for composing messages and validating emails
    but does not contain all the required functionality in order
    to send a message. Rather it should be subclassed for each different type of
    email service, and those subclasses should define an __init__
    method (to set any instance attributes such as credentials) and a _send_message
    method (to implement the actual sending of the message).

    For an example of this subclassing in practice, look at the Gmail notification
    connector in parsons.notifications.gmail.
    """

    log = logger

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def _send_message(self, message):
        pass

    def _create_message_simple(self, sender, to, subject, message_text):
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
            An object passable to send_message to send
        """
        self.log.info("Creating a simple message...")

        message = MIMEText(message_text)
        message["to"] = to
        message["from"] = sender
        message["subject"] = subject

        return message

    def _create_message_html(self, sender, to, subject, message_text, message_html):
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
            An object passable to send_message to send
        """
        self.log.info("Creating an html message...")

        message = MIMEMultipart("alternative")
        message["subject"] = subject
        message["from"] = sender
        message["to"] = to
        if message_text:
            message.attach(MIMEText(message_text, "plain"))
        message.attach(MIMEText(message_html, "html"))

        return message

    def _create_message_attachments(
        self, sender, to, subject, message_text, files, message_html=None
    ):
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
            An object passable to send_message to send
        """
        self.log.info("Creating a message with attachments...")

        message = MIMEMultipart("alternative")
        message["to"] = to
        message["from"] = sender
        message["subject"] = subject

        msg = MIMEText(message_text, "plain")
        message.attach(msg)

        if message_html:
            html = MIMEText(message_html, "html")
            message.attach(html)

        for f in files:
            filename = getattr(f, "name", "file")
            file_bytes = b""

            if isinstance(f, io.StringIO):
                file_bytes = f.getvalue().encode()
            elif isinstance(f, io.BytesIO):
                file_bytes = f.getvalue()
            else:
                filename = os.path.basename(f)
                fp = open(f, "rb")
                file_bytes = fp.read()
                fp.close()

            content_type, encoding = mimetypes.guess_type(filename)
            self.log.debug(f"(File: {f}, Content-type: {content_type}, " f"Encoding: {encoding})")

            if content_type is None or encoding is not None:
                content_type = "application/octet-stream"

            main_type, sub_type = content_type.split("/", 1)

            if main_type == "text":
                self.log.info("Added a text file.")
                msg = MIMEText(file_bytes, _subtype=sub_type, _charset="utf-8")

            elif main_type == "image":
                self.log.info("Added an image file.")
                msg = MIMEImage(file_bytes, _subtype=sub_type)
                msg.add_header("Content-ID", f"<{filename}>")

            elif main_type == "audio":
                self.log.info("Added an audio file.")
                msg = MIMEAudio(file_bytes, _subtype=sub_type)

            elif main_type == "application":
                self.log.info("Added an application file.")
                msg = MIMEApplication(file_bytes, _subtype=sub_type)

            else:
                self.log.info("Added an unknown-type file.")
                msg = MIMEBase(main_type, sub_type)
                msg.set_payload(file_bytes)
                encode_base64(msg)

            msg.add_header("Content-Disposition", "attachment", filename=filename)
            message.attach(msg)

        return message

    def _validate_email_string(self, str):
        self.log.debug(f"Validating email {str}...")
        realname, email_addr = parseaddr(str)

        if not email_addr:
            raise ValueError("Invalid email address.")

        if not validate_email(email_addr):
            raise ValueError("Invalid email address.")

        return True

    def send_email(self, sender, to, subject, message_text, message_html=None, files=None):
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
            None
        """
        self.log.info("Preparing to send an email...")

        self.log.info("Validating email(s)")
        if isinstance(to, list):
            if len(to) == 0:
                raise EmptyListError("Must contain at least 1 email.")

            for e in to:
                self._validate_email_string(e)

            to = ", ".join(to)

        elif isinstance(to, str):
            self._validate_email_string(to)

        if not message_html and not files:
            msg_type = "simple"
            msg = self._create_message_simple(sender, to, subject, message_text)

        elif not files:
            msg_type = "html"
            msg = self._create_message_html(sender, to, subject, message_text, message_html)
        else:
            msg_type = "attachments"
            if isinstance(files, str):
                files = [files]

            msg = self._create_message_attachments(
                sender, to, subject, message_text, files, message_html
            )

        self.log.info(f"Sending a(n) {msg_type} email...")

        self._send_message(msg)

        self.log.info("Email sent succesfully.")


class EmptyListError(IndexError):
    """Throw when a list is empty that should contain at least 1 element."""

    pass
