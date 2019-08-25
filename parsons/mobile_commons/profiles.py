"""Mobile Commons Profiles Endpoints."""


class Profiles(object):
    """Class for profiles endpoints."""

    def __init__(self, mc_connection):
        """Initialize the Profiles class.

        `Args:`
            mc_connection: MobileCommonsConnector
                The connector to access the Mobile Commons API.
        """
        self.connection = mc_connection

    def profiles(self, phone_number=None, from_date=None, to_date=None,
                 limit=None, page=None, include_custom_columns=None,
                 include_subscriptions=None, include_clicks=None,
                 include_members=None):
        """Return a list of profiles.

        `Args:`
            phone_number: list
                Optional; Limits the returned profiles matching the provided
                phone numbers. Phone numbers should be specified with country
                code.
            from_date: str
                Optional; Limits the returned profiles to ones updated after
                or on this date time. ISO-8601 format
            to_date: str
                Optional; Limits the returned profiles to ones updated before
                or on this date time. ISO-8601 forma
            limit: int
                Optional; Limits the number of returned profiles.
                Maximum of 1000
            page: int
                Optional; Specifies which page, of the total number of pages
                of results, to return
            include_custom_columns: boolean
                Optional; *Optional* default 'true' - allows exclusion of custom
                columns associated with profiles, pass 'false' to limit
            include_subscriptions: boolean
                Optional; *Optional* default 'true' - allows exclusion of
                subscriptions for each profile, pass 'false' to limit
            include_clicks: boolean
                Optional; *Optional* default 'true' - allows exclusion of clicks
            include_members: boolean
                Optional; *Optional* default 'true' - allows exclusion of
                profile member records maintained for integrations
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """
        url = self.connection.uri + 'profiles'

        if phone_number:
            phone_number = ','.join(phone_number)

        args = {'phone_number': phone_number,
                'from': from_date,
                'to': to_date,
                'limit': limit,
                'page': page,
                'include_custom_columns': include_custom_columns,
                'include_subscriptions': include_subscriptions,
                'include_clicks': include_clicks,
                'include_members': include_members}

        response = self.connection.request_paginate(
            url, 'profiles', args=args, resp_type='xml')

        if response:
            return self.connection.output(response)
        else:
            return None

    def profile_get(self, phone_number, company=None, include_messages=False,
                    include_donations=False):
        """Return a single profile record.

        `Args:`
            phone_number: str
                Required; The phone number for the profile to return.
            company: str
                Optional; If different that the one specified for the
                connection. Default is the firm.
            include_messages: boolean
                Optional; Set to true to include associated text messages.
                Default is false.
            include_donations: boolean
                Optional; Set to true to include associated mobile giving
                donations, if any. Default is false.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """
        url = self.connection.uri + 'profile'

        args = {'phone_number': phone_number,
                'company': company,
                'include_messages': include_messages,
                'include_donations': include_donations}

        response = self.connection.request(url, args=args, resp_type='xml')

        if response['response']['success'] == 'true':
            return self.connection.output(response['response']['profile'])
        else:
            return None

    def profile_update(self, phone_number, email=None, postal_code=None,
                       first_name=None, last_name=None, street1=None,
                       street2=None, city=None, state=None, country=None,
                       custom_fields={}, opt_in_path_id=None):
        """Create or update a profile.

        `Args:`
            phone_number: str
                Required; The phone number for the profile to update.
            email: str
                Optional; New email for the profile.
            postal_code: str
                Optional; New postal code for the profile.
            first_name: str
                Optional; New firstname for the profile.
            last_name: str
                Optional; New lastname for the profile.
            street1: str
                Optional; New street1 for the profile.
            street2: str
                Optional; New street2 for the profile.
            city: str
                Optional; New city for the profile.
            state: str
                Optional; New state for the profile.
            country: str
                Optional; New country for the profile.
            custom_fields: dict
                Optional; A dict of custom fields and their new values for the
                profile.
            opt_in_path_id: str
                Optional; New opt_in_path_id for the profile.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """
        url = self.connection.uri + 'profile_update'

        post_data = {
            'phone_number': phone_number,
            'email': email,
            'postal_code': postal_code,
            'first_name': first_name,
            'last_name': last_name,
            'street1': street1,
            'street2': street2,
            'city': city,
            'state': state,
            'country': country,
            'opt_in_path_id': opt_in_path_id}

        # Add each custom field as its own data point
        post_data.update(custom_fields)

        response = self.connection.request(
            url, req_type='POST', post_data=post_data, resp_type='xml')

        if response['response']['success'] == 'true':
            return self.connection.output(response['response']['profile'])
        else:
            return None

    def profile_opt_out(self, phone_number, campaign_id=None,
                        subscription_id=None):
        """Opt out a profile from a campaign, subscription or all.

        `Args:`
            phone_number: str
                Required; The phone number for the profile to opt out.
            campaign_id: int
                Optional; Opt-out this campaign only. Default is all campaigns.
            subscription_id:int
                Optional; Opt-out this subscription only. Default is all
                subscriptions.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """
        url = self.connection.uri + 'profile_opt_out'

        post_data = {'phone_number': phone_number,
                     'campaign_id': campaign_id,
                     'subscription_id': subscription_id}

        response = self.connection.request(
            url, req_type='POST', post_data=post_data, resp_type='xml')

        if response['response']['success'] == 'true':
            return self.connection.output(response['response']['profile'])
        else:
            return None
