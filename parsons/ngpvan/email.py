from parsons.etl.table import Table
import logging

logger = logging.getLogger(__name__)


class Email(object):
    """
    Instantiate the Email class.

    You can find the docs for the NGP VAN Email API here:
    https://docs.ngpvan.com/reference/email-overview
    """

    def __init__(self, van_connection):

        self.connection = van_connection

    def get_emails(self, ascending: bool = True) -> Table:
        """
        Get emails.

        `Args:`
            ascending : Bool
                sorts results in ascending or descending order
                for the dateModified field. Defaults to True (ascending).

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """
        if ascending:
            params = {
                "$orderby": "dateModified asc",
            }
        if not ascending:
            params = {
                "$orderby": "dateModified desc",
            }

        tbl = Table(self.connection.get_request("email/messages", params=params))
        logger.debug(f"Found {tbl.num_rows} emails.")
        return tbl

    def get_email(self, email_id: int, expand: bool = True) -> Table:
        """
        Get an email.

        Note that it takes some time for the system to aggregate opens and click-throughs,
        so data can be delayed up to 15 minutes.

        `Args:`
            email_id : int
                The email id.
            expand : bool
                Optional; expands the email message to include the email content and
                statistics. Defaults to True.

        `Returns:`
            dict
        """

        params = {
            "$expand": (
                "emailMessageContent, EmailMessageContentDistributions" if expand else None
            ),
        }

        r = self.connection.get_request(f"email/message/{email_id}", params=params)
        logger.debug(f"Found email {email_id}.")
        return r

    def get_email_stats(self) -> Table:
        """
        Get stats for all emails, aggregating any A/B tests.

        `Args:`
            emails : list
                A list of email message details.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        email_list = []

        final_email_list = []

        emails = self.get_emails()

        foreign_message_ids = [email["foreignMessageId"] for email in emails]

        for fmid in foreign_message_ids:
            email = self.get_email(fmid)
            email_list.append(email)

        for email in email_list:
            d = {}
            d["name"] = email["name"]
            d["createdBy"] = email["createdBy"]
            d["dateCreated"] = email["dateCreated"]
            d["dateModified"] = email["dateModified"]
            d["dateScheduled"] = email["dateScheduled"]
            d["foreignMessageId"] = email["foreignMessageId"]
            d["recipientCount"] = 0
            d["bounceCount"] = 0
            d["contributionCount"] = 0
            d["contributionTotal"] = 0
            d["formSubmissionCount"] = 0
            d["linksClickedCount"] = 0
            d["machineOpenCount"] = 0
            d["openCount"] = 0
            d["unsubscribeCount"] = 0
            try:
                for i in email["emailMessageContent"]:
                    d["recipientCount"] += i["emailMessageContentDistributions"]["recipientCount"]
                    d["bounceCount"] += i["emailMessageContentDistributions"]["bounceCount"]
                    d["contributionCount"] += i["emailMessageContentDistributions"][
                        "contributionCount"
                    ]
                    d["contributionTotal"] += i["emailMessageContentDistributions"][
                        "contributionTotal"
                    ]
                    d["formSubmissionCount"] += i["emailMessageContentDistributions"][
                        "formSubmissionCount"
                    ]
                    d["linksClickedCount"] += i["emailMessageContentDistributions"][
                        "linksClickedCount"
                    ]
                    d["machineOpenCount"] += i["emailMessageContentDistributions"][
                        "machineOpenCount"
                    ]
                    d["openCount"] += i["emailMessageContentDistributions"]["openCount"]
                    d["unsubscribeCount"] += i["emailMessageContentDistributions"][
                        "unsubscribeCount"
                    ]
            except TypeError as e:
                logger.info(str(e))
                pass

            final_email_list.append(d)

        return Table(final_email_list)
