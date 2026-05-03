import logging
from datetime import datetime

from parsons import Table
from parsons.capitol_canary import CapitolCanary

logger = logging.getLogger(__name__)


class Phone2Action:
    """
    Instantiate Phone2Action Class.

    Args:
        app_id:
            The Phone2Action provided application id.
            Not required if ``PHONE2ACTION_APP_ID`` env variable set.
        app_key:
            The Phone2Action provided application key.
            Not required if ``PHONE2ACTION_APP_KEY`` env variable set.

    """

    def __init__(self, app_id: str | None = None, app_key: str | None = None) -> None:
        self.capitol_canary = CapitolCanary(app_id, app_key)
        logger.warning("The Phone2Action class is being deprecated and replaced by CapitalCanary")

    def __getattr__(self, name):
        try:
            return getattr(self.capitol_canary, name)
        except AttributeError as e:
            raise AttributeError(f"{type(self).__name__} object has no attribute {name}") from e

    def get_advocates(
        self,
        state: str | None = None,
        campaign_id: int | None = None,
        updated_since: str | int | datetime | None = None,
        page: int | None = None,
    ) -> dict[str, Table]:
        """
        Return advocates (person records).

        If no page is specified, the method will automatically paginate through the available
        advocates.

        Args:
            state:
                Filter by US postal abbreviation for a state or territory.
                E.g. ``CA``, ``NY``, or ``DC``.
            campaign_id:
                Filter to specific campaign.
            updated_since:
                Fetch all advocates updated since the date provided.
                This can be a datetime object, a UNIX timestamp,
                or a date string (ex. ``2014-01-05 23:59:43``)
            page:
                Page number of data to fetch.
                If this is specified, call will only return one page.

        Returns:
            A dict of parsons tables.

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
        state: str | None = None,
        zip: int | None = None,
        include_generic: bool = False,
        include_private: bool = False,
        include_content: bool = True,
    ) -> Table:
        """
        Returns a list of campaigns

        Args:
            state:
                Filter by US postal abbreviation for a state or territory.
                E.g. ``CA``, ``NY`` or ``DC``.
            zip:
                Filter by 5 digit zip code.
            include_generic:
                When filtering by state or ZIP code, include unrestricted campaigns.
            include_private:
                If ``True``, will include private campaigns in results.
            include_content:
                If ``True``, include campaign content fields, which may vary.
                This may cause sync errors.


        """
        return self.capitol_canary.get_campaigns(
            state, zip, include_generic, include_private, include_content
        )

    def create_advocate(
        self,
        campaigns: list,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        address1: str | None = None,
        address2: str | None = None,
        city: str | None = None,
        state: str | None = None,
        zip5: str | None = None,
        sms_optin: bool | None = None,
        email_optin: bool | None = None,
        sms_optout: bool | None = None,
        email_optout: bool | None = None,
        **kwargs,
    ) -> int:
        """
        Create an advocate.

        If you want to opt an advocate into or out of SMS / email campaigns, you must provide
        the email address or phone number (accordingly).

        The list of arguments only partially covers the fields that can be set on the advocate.
        For a complete list of fields that can be updated, see the `Phone2Action API Create Advocate Documentation`_.

        Args:
            campaigns: The ID(s) of campaigns to add the advocate to
            first_name: The first name of the advocate
            last_name: The last name of the advocate
            email:
                An email address to add for the advocate.
                One of ``email`` or ``phone`` is required.
            phone:
                An phone # to add for the advocate.
                One of ``email`` or ``phone`` is required.
            address1: The first line of the advocates' address
            address2: The second line of the advocates' address
            city: The city of the advocates address
            state: The state of the advocates address
            zip5: The 5 digit Zip code of the advocate
            sms_optin:
                Whether to opt the advocate into receiving text messages.
                An SMS confirmation text message will be sent.
                You must provide values for the `phone` and `campaigns` arguments.
            email_optin:
                Whether to opt the advocate into receiving emails.
                You must provide values for the `email` and `campaigns` arguments.
            sms_optout:
                Whether to opt the advocate out of receiving text messages.
                You must provide values for the `phone` and `campaigns` arguments.
                Once an advocate is opted out, they cannot be opted back in.
            email_optout:
                Whether to opt the advocate out of receiving emails.
                You must provide values for the `email` and `campaigns` arguments.
                Once an advocate is opted out, they cannot be opted back in.
            `**kwargs`: Additional fields on the advocate to update

        Returns:
            ID of the created advocate.

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
        advocate_id: int,
        campaigns: list | None = None,
        email: str | None = None,
        phone: str | None = None,
        sms_optin: bool | None = None,
        email_optin: bool | None = None,
        sms_optout: bool | None = None,
        email_optout: bool | None = None,
        **kwargs,
    ) -> None:
        """
        Update the fields of an advocate.

        If you want to opt an advocate into or out of SMS / email campaigns, you must provide
        the email address or phone number along with a list of campaigns.

        The list of arguments only partially covers the fields that can be updated on the advocate.
        For a complete list of fields that can be updated, see the `Phone2Action API Create Advocate Documentation`_.

        Args:
            advocate_id: The ID of the advocate being updates
            campaigns: The ID(s) of campaigns to add the user to
            email: An email address to add for the advocate (or to use when opting in/out)
            phone: An phone # to add for the advocate (or to use when opting in/out)
            sms_optin:
                Whether to opt the advocate into receiving text messages.
                An SMS confirmation text message will be sent.
                You must provide values for the ``phone`` and ``campaigns`` arguments.
            email_optin:
                Whether to opt the advocate into receiving emails.
                You must provide values for the ``email`` and ``campaigns`` arguments.
            sms_optout:
                Whether to opt the advocate out of receiving text messages.
                You must provide values for the ``phone`` and ``campaigns`` arguments.
                Once an advocate is opted out, they cannot be opted back in.
            email_optout:
                Whether to opt the advocate out of receiving emails.
                You must provide values for the ``email`` and ``campaigns`` arguments.
                Once an advocate is opted out, they cannot be opted back in.
            `**kwargs`: Additional fields on the advocate to update

        """
        self.capitol_canary.update_advocate(
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
