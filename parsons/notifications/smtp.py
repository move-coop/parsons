import smtplib

from parsons.notifications.sendmail import SendMail
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
        host=None,
        port=None,
        username=None,
        password=None,
        tls=None,
        ssl=None,
        close_manually=False,
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

    def _send_message(self, message):
        """Send an email message.

        Args:
            message: `MIME object <https://docs.python.org/2/library/email.mime.html>`
                i.e. the objects created by the create_* instance methods
        Returns:
            dict of refused To addresses (otherwise None)

        """
        self.log.info("Sending a message...")
        try:
            conn = self.get_connection()
            result = conn.sendmail(
                message["From"],
                [x.strip() for x in message["To"].split(",")],
                message.as_string(),
            )
        except Exception:
            self.log.exception("An error occurred: while attempting to send a message.")
            raise

        if result:
            self.log.warning("Message failed to send to some recipients: " + str(result))
        if not self.close_manually:
            conn.quit()
            self.conn = None
        return result

    def _infer_port(self):
        """Assume port number based on security protocol used."""
        if self.ssl:
            self.port = 465
        elif self.tls:
            self.port = 587
        else:
            self.port = 25
