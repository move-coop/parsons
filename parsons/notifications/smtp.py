import contextlib
import smtplib
from email.message import Message
from email.utils import getaddresses

from parsons.notifications.sendmail import EmptyListError, SendMail
from parsons.utilities import check_env

TRUE_VALUES = ("true", "True", "1", True)
FALSE_VALUES = ("false", "False", "0", False)


class SMTP(SendMail):
    """
    Create a SMTP object, for sending emails.

    Args:
        host: str
            The host of the SMTP server
        port: int
            The port of the SMTP server (Default is 587 for TLS)
        username: str
            The username of the SMTP server login
        password: str
            The password of the SMTP server login
        tls: bool
            Defaults to True -- Can set SMTP_TLS to "0" or "False" to disable
            If SSL is True, TLS is disabled.
        ssl: bool
            Defaults to False -- Can set SMTP_SSL to "1" or "True" to enable
        close_manually: bool
            When set to True, send_message will not close the connection

    """

    def __init__(
        self,
        host: str | None = None,
        port: int | str | None = None,
        username: str | None = None,
        password: str | None = None,
        *,
        tls: bool | None = None,
        ssl: bool | None = None,
        close_manually: bool = False,
    ):
        self.tls = check_env.check("SMTP_TLS", tls, optional=True) not in FALSE_VALUES
        self.ssl = check_env.check("SMTP_SSL", ssl, optional=True) in TRUE_VALUES

        self.host = check_env.check("SMTP_HOST", host)
        self.port = int(check_env.check("SMTP_PORT", port, optional=True) or self._infer_port())

        self.username = check_env.check("SMTP_USER", username)
        self.password = check_env.check("SMTP_PASSWORD", password)

        self.close_manually = close_manually

        self.conn = None

    def get_connection(self):
        """
        Get the active SMTP connection.

        If there is no active connection, initialize one.
        """
        if self.conn is None:
            if self.ssl:
                self.conn = smtplib.SMTP_SSL(self.host, self.port)
            else:
                self.conn = smtplib.SMTP(self.host, self.port)
                self.conn.ehlo()

                if self.tls:
                    self.conn.starttls()
                    self.conn.ehlo()

            if self.username and self.password:
                self.conn.login(self.username, self.password)

        return self.conn

    def quit(self):
        """
        Close the connection manually.

        Typically used if SMTP was initialized with close_manually=True.
        """
        if not self.conn:
            return

        try:
            self.conn.quit()

        except (OSError, smtplib.SMTPException):
            with contextlib.suppress(Exception):
                self.conn.close()

        finally:
            self.conn = None

    def _send_message(self, message: Message) -> dict:
        """
        Send an email message.

        Args:
            message: email.message.Message
                A Message object to be sent.

        Returns:
            dict of refused recipient addresses (otherwise None)

        Raises:
            EmptyListError
                If there are no recipients across to, cc, and bcc.

        """
        tos = message.get_all("To") or []
        ccs = message.get_all("Cc") or []
        bccs = message.get_all("Bcc") or []
        if "Bcc" in message:
            del message["Bcc"]

        all_recipients = [addr for _, addr in getaddresses(tos + ccs + bccs)]
        if not all_recipients:
            err_msg = "No recipients found in To, Cc, or Bcc headers."
            raise EmptyListError(err_msg)

        self.log.info("Sending a message...")
        conn = self.get_connection()
        try:
            result = conn.sendmail(message["From"], all_recipients, message.as_string())
            if result:
                self.log.warning("Message failed for some recipients: %s", result)
                return result

        except Exception:
            self.log.exception("An error occurred while attempting to send a message.")
            self.quit()
            raise

        finally:
            if not self.close_manually:
                self.quit()

    def _infer_port(self):
        """Set active port by assuming port number based on security protocol used."""
        if self.ssl:
            self.port = 465
        elif self.tls:
            self.port = 587
        else:
            self.port = 25
