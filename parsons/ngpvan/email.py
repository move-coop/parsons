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

    def get_email_stats(self, aggregate_ab: bool = True) -> Table:
        """
        Get stats for all emails, aggregating any A/B tests.

        `Args:`
            aggregate_ab : bool
                If A/B test results for emails should get aggregated.

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

        # Outside and inside emailMessageContentDistributions field
        outer_fields = [
            "name",
            "createdBy",
            "dateCreated",
            "dateModified",
            "dateScheduled",
            "foreignMessageId",
        ]
        inner_fields = [
            "recipientCount",
            "bounceCount",
            "contributionCount",
            "contributionTotal",
            "formSubmissionCount",
            "linksClickedCount",
            "machineOpenCount",
            "openCount",
            "unsubscribeCount",
            # "subject"  # included here for clarity, but has some special logic
        ]
        # If we are aggregating, we have one entry per foreignMessageId (outer loop) and
        # sum over the values inside the inner loop. If we are not, then we need to loop
        # over foreignMessageId and each component of emailMessageContent, so we loop
        # over both and pull out data (with no aggregation) for each.
        if aggregate_ab:
            for email in email_list:  # One row per foreignMessageId
                outer = {field: email[field] for field in outer_fields}
                inner = {field: 0 for field in inner_fields}
                for i in email["emailMessageContent"]:
                    try:
                        for field in inner_fields:  # Aggregation of all inner values
                            inner[field] += i["emailMessageContentDistributions"][field]
                        # Just replacing subject to get the last one
                        inner["subject"] = i["subject"]
                    except KeyError as e:
                        logger.info(str(e))
                        pass
                final_email_list.append({**outer, **inner})
        else:
            for email in email_list:
                for i in email["emailMessageContent"]:
                    # One row per foreignMessageId / emailMessageContent entry
                    outer = {field: email[field] for field in outer_fields}
                    inner = {field: 0 for field in inner_fields}
                    try:
                        for field in inner_fields:
                            inner[field] = i["emailMessageContentDistributions"][field]
                        inner["subject"] = i["subject"]
                    except KeyError as e:
                        logger.info(str(e))
                    final_email_list.append({**outer, **inner})

        return Table(final_email_list)
