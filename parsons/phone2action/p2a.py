from parsons.capitol_canary import CapitolCanary
import logging

logger = logging.getLogger(__name__)


class Phone2Action(object):
    """
    Instantiate Phone2Action Class

    `Args:`
        app_id: str
            The Phone2Action provided application id. Not required if ``PHONE2ACTION_APP_ID``
            env variable set.
        app_key: str
            The Phone2Action provided application key. Not required if ``PHONE2ACTION_APP_KEY``
            env variable set.
    `Returns:`
        Phone2Action Class
    """

    def __init__(self, app_id=None, app_key=None):
        self.capitol_canary = CapitolCanary(app_id, app_key)
        logger.warning("The Phone2Action class is being deprecated and replaced by CapitalCanary")

    def __getattr__(self, name):
        try:
            return getattr(self.capitol_canary, name)
        except AttributeError:
            raise AttributeError(f"{type(self).__name__} object has no attribute {name}")

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
        return self.capitol_canary.get_advocates(state, campaign_id, updated_since, page)

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

        return self.capitol_canary.get_campaigns(
            state, zip, include_generic, include_private, include_content
        )

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
        `the Phone2Action API documentation <https://docs.phone2action.com/#calls-create>`_.

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
        return self.capitol_canary.create_advocate(
            campaigns,
            first_name,
            last_name,
            email,
            phone,
            address1,
            address2,
            city,
            state,
            zip5,
            sms_optin,
            email_optin,
            sms_optout,
            email_optout,
            **kwargs,
        )

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
        `the Phone2Action API documentation <https://docs.phone2action.com/#calls-create>`_.

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
        return self.capitol_canary.update_advocate(
            advocate_id,
            campaigns,
            email,
            phone,
            sms_optin,
            email_optin,
            sms_optout,
            email_optout,
            **kwargs,
        )
