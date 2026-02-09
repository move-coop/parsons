import logging

from parsons.capitol_canary import CapitolCanary

logger = logging.getLogger(__name__)


class Phone2Action:
    """
    Instantiate Phone2Action Class.

    Args:
        app_id (str, optional): The Phone2Action provided application id. Not required if
            ``PHONE2ACTION_APP_ID`` env variable set. Defaults to None.
        app_key (str, optional): The Phone2Action provided application key. Not required if
            ``PHONE2ACTION_APP_KEY`` env variable set. Defaults to None.

    Returns:
        Phone2Action Class

    """

    def __init__(self, app_id=None, app_key=None):
        self.capitol_canary = CapitolCanary(app_id, app_key)
        logger.warning("The Phone2Action class is being deprecated and replaced by CapitalCanary")

    def __getattr__(self, name):
        try:
            return getattr(self.capitol_canary, name)
        except AttributeError as e:
            raise AttributeError(f"{type(self).__name__} object has no attribute {name}") from e

    def get_advocates(self, state=None, campaign_id=None, updated_since=None, page=None):
        """
        Return advocates (person records).

        If no page is specified, the method will automatically paginate through the available advocates.

        Args:
            state (str, optional): Filter by US postal abbreviation for a state or territory e.g., "CA" "NY" or
                "DC". Defaults to None.
            campaign_id (int, optional): Filter to specific campaign. Defaults to None.
            updated_since (Str | int | datetime, optional): Fetch all advocates updated since the date provided;
                this can be a datetime object, a UNIX timestamp, or a date string (ex.
                '2014-01-05 23:59:43'). Defaults to None.
            page (int, optional): Page number of data to fetch; if this is specified, call will only return one
                page. Defaults to None.

        Returns:
            A dict of parsons tables:
                * emails
                * phones
                * memberships
                * tags
                * ids
                * fields
                * advocates.

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
        Returns a list of campaigns.

        Args:
            state (str, optional): Filter by US postal abbreviation for a state or territory e.g., "CA" "NY" or
                "DC". Defaults to None.
            zip (int, optional): Filter by 5 digit zip code. Defaults to None.
            include_generic (bool, optional): When filtering by state or ZIP code, include unrestricted campaigns.
                Defaults to False.
            include_private (bool, optional): If true, will include private campaigns in results.
                Defaults to False.
            include_content (bool, optional): If true, include campaign content fields, which may vary.
                This may cause sync errors. Defaults to True.

        Returns:
            Table: See :ref:`parsons-table` for output options.

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

        If you want to opt an advocate into or out of SMS / email campaigns, you must provide the email address or phone
        number (accordingly).

        The list of arguments only partially covers the fields that can be set on the advocate.
        For a complete list of fields that can be updated, see
        `the Phone2Action API documentation <https://docs.phone2action.com/#calls-create>`_.

        Args:
            campaigns: List The ID(s) of campaigns to add the advocate to.
            first_name (str, optional): The first name of the advocate. Defaults to None.
            last_name (str, optional): The last name of the advocate. Defaults to None.
            email (str, optional): An email address to add for the advocate. One of ``email`` or ``phone`` is
                required. Defaults to None.
            phone (str, optional): An phone # to add for the advocate. One of ``email`` or ``phone`` is required.
                Defaults to None.
            address1 (str, optional): The first line of the advocates' address. Defaults to None.
            address2 (str, optional): The second line of the advocates' address. Defaults to None.
            city (str, optional): The city of the advocates address. Defaults to None.
            state (str, optional): The state of the advocates address. Defaults to None.
            zip5 (str, optional): The 5 digit Zip code of the advocate. Defaults to None.
            sms_optin (bool, optional): Whether to opt the advocate into receiving text messages; an SMS
                confirmation text message will be sent. You must provide values for the ``phone`` and ``campaigns``
                arguments. Defaults to None.
            email_optin (bool, optional): Whether to opt the advocate into receiving emails.
                You must provide values for the ``email`` and ``campaigns`` arguments. Defaults to None.
            sms_optout (bool, optional): Whether to opt the advocate out of receiving text messages.
                You must provide values for the ``phone`` and ``campaigns`` arguments. Once an advocate is opted out,
                they cannot be opted back in. Defaults to None.
            email_optout (bool, optional): Whether to opt the advocate out of receiving emails.
                You must provide values for the ``email`` and ``campaigns`` arguments. Once an advocate is opted out,
                they cannot be opted back in. Defaults to None.
            **kwargs: Additional fields on the advocate to update.

        Returns:
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

        If you want to opt an advocate into or out of SMS / email campaigns, you must provide the email address or phone
        number along with a list of campaigns.

        The list of arguments only partially covers the fields that can be updated on the advocate.
        For a complete list of fields that can be updated, see
        `the Phone2Action API documentation <https://docs.phone2action.com/#calls-create>`_.

        Args:
            advocate_id: Integer The ID of the advocate being updates.
            campaigns (list, optional): The ID(s) of campaigns to add the user to. Defaults to None.
            email (str, optional): An email address to add for the advocate (or to use when opting in/out).
                Defaults to None.
            phone (str, optional): An phone # to add for the advocate (or to use when opting in/out).
                Defaults to None.
            sms_optin (bool, optional): Whether to opt the advocate into receiving text messages; an SMS
                confirmation text message will be sent. You must provide values for the ``phone`` and ``campaigns``
                arguments. Defaults to None.
            email_optin (bool, optional): Whether to opt the advocate into receiving emails.
                You must provide values for the ``email`` and ``campaigns`` arguments. Defaults to None.
            sms_optout (bool, optional): Whether to opt the advocate out of receiving text messages.
                You must provide values for the ``phone`` and ``campaigns`` arguments. Once an advocate is opted out,
                they cannot be opted back in. Defaults to None.
            email_optout (bool, optional): Whether to opt the advocate out of receiving emails.
                You must provide values for the ``email`` and ``campaigns`` arguments. Once an advocate is opted out,
                they cannot be opted back in. Defaults to None.
            **kwargs: Additional fields on the advocate to update.

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
