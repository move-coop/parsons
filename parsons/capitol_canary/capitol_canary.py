from requests.auth import HTTPBasicAuth
from parsons.etl import Table
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector
from parsons.utilities.datetime import date_to_timestamp
import logging

logger = logging.getLogger(__name__)

CAPITOL_CANARY_URI = "https://api.phone2action.com/2.0/"


class CapitolCanary(object):
    """
    Instantiate CapitolCanary Class

    `Args:`
        app_id: str
            The CapitolCanary provided application id. Not required if ``CAPITOLCANARY_APP_ID``
            env variable set.
        app_key: str
            The CapitolCanary provided application key. Not required if ``CAPITOLCANARY_APP_KEY``
            env variable set.
    `Returns:`
        CapitolCanary Class
    """

    def __init__(self, app_id=None, app_key=None):
        # check first for CapitolCanary branded app key and ID
        cc_app_id = check_env.check("CAPITOLCANARY_APP_ID", None, optional=True)
        cc_app_key = check_env.check("CAPITOLCANARY_APP_KEY", None, optional=True)

        self.app_id = cc_app_id or check_env.check("PHONE2ACTION_APP_ID", app_id)
        self.app_key = cc_app_key or check_env.check("PHONE2ACTION_APP_KEY", app_key)
        self.auth = HTTPBasicAuth(self.app_id, self.app_key)
        self.client = APIConnector(CAPITOL_CANARY_URI, auth=self.auth)

    def _paginate_request(self, url, args=None, page=None):
        # Internal pagination method

        if page is not None:
            args["page"] = page

        r = self.client.get_request(url, params=args)

        json = r["data"]

        if page is not None:
            return json

        # If count of items is less than the total allowed per page, paginate
        while r["pagination"]["count"] == r["pagination"]["per_page"]:

            r = self.client.get_request(r["pagination"]["next_url"], args)
            json.extend(r["data"])

        return json

    def get_advocates(self, state=None, campaign_id=None, updated_since=None, page=None):
        """
        Return advocates (person records).

        If no page is specified, the method will automatically paginate through the available
        advocates.

        `Args:`
            state: str
                Filter by US postal abbreviation for a state
                or territory e.g., "CA" "NY" or "DC"
            campaign_id: int
                Filter to specific campaign
            updated_since: str or int or datetime
                Fetch all advocates updated since the date provided; this can be a datetime
                object, a UNIX timestamp, or a date string (ex. '2014-01-05 23:59:43')
            page: int
                Page number of data to fetch; if this is specified, call will only return one
                page.
        `Returns:`
            A dict of parsons tables:
                * emails
                * phones
                * memberships
                * tags
                * ids
                * fields
                * advocates
        """

        # Convert the passed in updated_since into a Unix timestamp (which is what the API wants)
        updated_since = date_to_timestamp(updated_since)

        args = {
            "state": state,
            "campaignid": campaign_id,
            "updatedSince": updated_since,
        }

        logger.info("Retrieving advocates...")
        json = self._paginate_request("advocates", args=args, page=page)

        return self._advocates_tables(Table(json))

    def _advocates_tables(self, tbl):
        # Convert the advocates nested table into multiple tables

        tbls = {
            "advocates": tbl,
            "emails": Table(),
            "phones": Table(),
            "memberships": Table(),
            "tags": Table(),
            "ids": Table(),
            "fields": Table(),
        }

        if not tbl:
            return tbls

        logger.info(f"Retrieved {tbl.num_rows} advocates...")

        # Unpack all of the single objects
        # The CapitolCanary API docs says that created_at and updated_at are dictionaries, but
        # the data returned from the server is a ISO8601 timestamp. - EHS, 05/21/2020
        for c in ["address", "districts"]:
            tbl.unpack_dict(c)

        # Unpack all of the arrays
        child_tables = [child for child in tbls.keys() if child != "advocates"]
        for c in child_tables:
            tbls[c] = tbl.long_table(["id"], c, key_rename={"id": "advocate_id"})

        return tbls

    def get_campaigns(
        self,
        state=None,
        zip=None,
        include_generic=False,
        include_private=False,
        include_content=True,
    ):
        """
        Returns a list of campaigns

        `Args:`
            state: str
                Filter by US postal abbreviation for a state or territory e.g., "CA" "NY" or "DC"
            zip: int
                Filter by 5 digit zip code
            include_generic: boolean
                When filtering by state or ZIP code, include unrestricted campaigns
            include_private: boolean
                If true, will include private campaigns in results
            include_content: boolean
                If true, include campaign content fields, which may vary. This may cause
                sync errors.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        args = {
            "state": state,
            "zip": zip,
            "includeGeneric": str(include_generic),
            "includePrivate": str(include_private),
        }

        tbl = Table(self.client.get_request("campaigns", params=args))
        if tbl:
            tbl.unpack_dict("updated_at")
            if include_content:
                tbl.unpack_dict("content")

        return tbl

    def create_advocate(
        self,
        campaigns,
        first_name=None,
        last_name=None,
        email=None,
        phone=None,
        address1=None,
        address2=None,
        city=None,
        state=None,
        zip5=None,
        sms_optin=None,
        email_optin=None,
        sms_optout=None,
        email_optout=None,
        **kwargs,
    ):
        """
        Create an advocate.

        If you want to opt an advocate into or out of SMS / email campaigns, you must provide
        the email address or phone number (accordingly).

        The list of arguments only partially covers the fields that can be set on the advocate.
        For a complete list of fields that can be updated, see
        `the CapitolCanary API documentation <https://docs.phone2action.com/#calls-create>`_.

        `Args:`
            campaigns: list
                The ID(s) of campaigns to add the advocate to
            first_name: str
                `Optional`; The first name of the advocate
            last_name: str
                `Optional`; The last name of the advocate
            email: str
                `Optional`; An email address to add for the advocate. One of ``email`` or ``phone``
                is required.
            phone: str
                `Optional`; An phone # to add for the advocate. One of ``email`` or ``phone`` is
                required.
            address1: str
                `Optional`; The first line of the advocates' address
            address2: str
                `Optional`; The second line of the advocates' address
            city: str
                `Optional`; The city of the advocates address
            state: str
                `Optional`; The state of the advocates address
            zip5: str
                `Optional`; The 5 digit Zip code of the advocate
            sms_optin: boolean
                `Optional`; Whether to opt the advocate into receiving text messages; an SMS
                confirmation text message will be sent. You must provide values for the ``phone``
                and ``campaigns`` arguments.
            email_optin: boolean
                `Optional`; Whether to opt the advocate into receiving emails. You must provide
                values for the ``email`` and ``campaigns`` arguments.
            sms_optout: boolean
                `Optional`; Whether to opt the advocate out of receiving text messages. You must
                provide values for the ``phone`` and ``campaigns`` arguments. Once an advocate is
                opted out, they cannot be opted back in.
            email_optout: boolean
                `Optional`; Whether to opt the advocate out of receiving emails. You must
                provide values for the ``email`` and ``campaigns`` arguments. Once an advocate is
                opted out, they cannot be opted back in.
            **kwargs:
                Additional fields on the advocate to update
        `Returns:`
            The int ID of the created advocate.
        """

        # Validate the passed in arguments

        if not campaigns:
            raise ValueError("When creating an advocate, you must specify one or more campaigns.")

        if not email and not phone:
            raise ValueError(
                "When creating an advocate, you must provide an email address or a phone number."
            )

        if (sms_optin or sms_optout) and not phone:
            raise ValueError(
                "When opting an advocate in or out of SMS messages, you must specify a valid "
                "phone and one or more campaigns"
            )

        if (email_optin or email_optout) and not email:
            raise ValueError(
                "When opting an advocate in or out of email messages, you must specify a valid "
                "email address and one or more campaigns"
            )

        # Align our arguments with the expected parameters for the API
        payload = {
            "email": email,
            "phone": phone,
            "firstname": first_name,
            "lastname": last_name,
            "address1": address1,
            "address2": address2,
            "city": city,
            "state": state,
            "zip5": zip5,
            "smsOptin": 1 if sms_optin else None,
            "emailOptin": 1 if email_optin else None,
            "smsOptout": 1 if sms_optout else None,
            "emailOptout": 1 if email_optout else None,
        }

        # Clean up any keys that have a "None" value
        payload = {key: val for key, val in payload.items() if val is not None}

        # Merge in any kwargs
        payload.update(kwargs)

        # Turn into a list of items so we can append multiple campaigns
        campaign_keys = [("campaigns[]", val) for val in campaigns]
        data = [(key, value) for key, value in payload.items()] + campaign_keys

        # Call into the CapitolCanary API
        response = self.client.post_request("advocates", data=data)
        return response["advocateid"]

    def update_advocate(
        self,
        advocate_id,
        campaigns=None,
        email=None,
        phone=None,
        sms_optin=None,
        email_optin=None,
        sms_optout=None,
        email_optout=None,
        **kwargs,
    ):
        """
        Update the fields of an advocate.

        If you want to opt an advocate into or out of SMS / email campaigns, you must provide
        the email address or phone number along with a list of campaigns.

        The list of arguments only partially covers the fields that can be updated on the advocate.
        For a complete list of fields that can be updated, see
        `the CapitolCanary API documentation <https://docs.phone2action.com/#calls-create>`_.

        `Args:`
            advocate_id: integer
                The ID of the advocate being updates
            campaigns: list
                `Optional`; The ID(s) of campaigns to add the user to
            email: str
                `Optional`; An email address to add for the advocate (or to use when opting in/out)
            phone: str
                `Optional`; An phone # to add for the advocate (or to use when opting in/out)
            sms_optin: boolean
                `Optional`; Whether to opt the advocate into receiving text messages; an SMS
                confirmation text message will be sent. You must provide values for the ``phone``
                and ``campaigns`` arguments.
            email_optin: boolean
                `Optional`; Whether to opt the advocate into receiving emails. You must provide
                values for the ``email`` and ``campaigns`` arguments.
            sms_optout: boolean
                `Optional`; Whether to opt the advocate out of receiving text messages. You must
                provide values for the ``phone`` and ``campaigns`` arguments. Once an advocate is
                opted out, they cannot be opted back in.
            email_optout: boolean
                `Optional`; Whether to opt the advocate out of receiving emails. You must
                provide values for the ``email`` and ``campaigns`` arguments. Once an advocate is
                opted out, they cannot be opted back in.
            **kwargs:
                Additional fields on the advocate to update
        """

        # Validate the passed in arguments
        if (sms_optin or sms_optout) and not (phone and campaigns):
            raise ValueError(
                "When opting an advocate in or out of SMS messages, you must specify a valid "
                "phone and one or more campaigns"
            )

        if (email_optin or email_optout) and not (email and campaigns):
            raise ValueError(
                "When opting an advocate in or out of email messages, you must specify a valid "
                "email address and one or more campaigns"
            )

        # Align our arguments with the expected parameters for the API
        payload = {
            "advocateid": advocate_id,
            "campaigns": campaigns,
            "email": email,
            "phone": phone,
            "smsOptin": 1 if sms_optin else None,
            "emailOptin": 1 if email_optin else None,
            "smsOptout": 1 if sms_optout else None,
            "emailOptout": 1 if email_optout else None,
            # remap first_name / last_name to be consistent with updated_advocates
            "firstname": kwargs.pop("first_name", None),
            "lastname": kwargs.pop("last_name", None),
        }

        # Clean up any keys that have a "None" value
        payload = {key: val for key, val in payload.items() if val is not None}

        # Merge in any kwargs
        payload.update(kwargs)

        # Turn into a list of items so we can append multiple campaigns
        campaigns = campaigns or []
        campaign_keys = [("campaigns[]", val) for val in campaigns]
        data = [(key, value) for key, value in payload.items()] + campaign_keys

        # Call into the CapitolCanary API
        self.client.post_request("advocates", data=data)
