class FakeSMTPConnection:
    """A stand-in for an ``smtplib.SMTP`` connection.

    Implements the slice of the interface the SMTP connector uses (``sendmail``
    and ``quit``) and records what it was asked to do so tests can assert on it.
    """

    def __init__(self):
        self.result = None
        self.quit_ran = False

    def sendmail(self, sender, to, message_body):
        self.result = (sender, to, message_body)
        if "willfail@example.com" in to:
            return {"willfail@example.com": (550, "User unknown")}
        return None

    def quit(self):
        self.quit_ran = True
