"""Mobile Commons Groups Endpoints."""


class Groups(object):
    """Class for groups endpoints."""

    def __init__(self, mc_connection):
        """Initialize the Groups class.

        `Args:`
            mc_connection: MobileCommonsConnector
                The connector to access the Mobile Commons API.
        """
        self.connection = mc_connection

    def groups(self):
        """Return a list of groups.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """
        url = self.connection.uri + 'groups'

        response = self.connection.request(url, resp_type='xml')

        if response['response']['success'] == 'true':
            if response['response']['groups']:
                return self.connection.output(
                    response['response']['groups']['group'])
            else:
                return None
        else:
            return None

    def group_members(self, group_id, limit=None, page=None, from_date=None,
                      to_date=None):
        """Return a list of members in a group.

        `Args:`
            group_id: int
                Required; The primary key of the group.
            limit: int
                Optional; Limits the number of returned profiles. Maximum of
                1000.
            page: int
                Optional; Specifies which page, of the total number of pages of
                results, to return.
            from_date: str
                Optional; Limits the returned profiles to ones updated after or
                on this date time. ISO-8601 format.
            to_date: str
                Optional; Limits the returned profiles to ones updated before
                or on this date time. ISO-8601 format.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """
        url = self.connection.uri + 'group_members'

        args = {'group_id': group_id,
                'limit': limit,
                'page': page,
                'from': from_date,
                'to': to_date}

        # TODO check with MC about pagination

        response = self.connection.request(url, args=args, resp_type='xml')

        if response['response']['success'] == 'true':
            if response['response']['group']:
                return self.connection.output(
                    response['response']['group']['profile'])
            else:
                return None
        else:
            return None

    def group_create(self, name):
        """Create a group.

        `Args:`
            name: str
                Required; The name for the new group.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """
        url = self.connection.uri + 'create_group'

        args = {'name': name}

        response = self.connection.request(url, args=args, resp_type='xml')

        if response['response']['success'] == 'true':
            if response['response']['group']:
                return self.connection.output(response['response']['group'])
            else:
                return None
        else:
            return None

    def group_add_members(self, group_id, phone_numbers):
        """Add a list of members to a group.

        `Args:`
            group_id: int
                Required; The primary key of the group.
            phone_numbers: list
                Required; A list of phone numbers to add to the group.
                If the phone numbers don't exist, the will be created as
                new profiles.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """
        url = self.connection.uri + 'add_group_member'

        if len(phone_numbers) == 0:
            raise ValueError("At least 1 phone number is required.")

        if phone_numbers:
            phone_number = ','.join(phone_numbers)

        args = {'group_id': group_id,
                'phone_number': phone_number}

        response = self.connection.request(url, args=args, resp_type='xml')

        if response['response']['success'] == 'true':
            if response['response']['group']:
                return self.connection.output(response['response']['group'])
            else:
                return None
        else:
            return None

    def group_remove_members(self, group_id, phone_number):
        """Remove a list of members from a group.

        `Args:`
            group_id: int
                Required; The primary key of the group.
            phone_number: list
                Required; A list of phone numbers to remove from the group.
                If the phone number is not a member of the group, it will
                still return the group.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """
        url = self.connection.uri + 'remove_group_member'

        if len(phone_number) == 0:
            raise ValueError("At least 1 phone number is required.")

        if phone_number:
            phone_number = ','.join(phone_number)

        args = {'group_id': group_id,
                'phone_number': phone_number}

        response = self.connection.request(url, args=args, resp_type='xml')

        if response['response']['success'] == 'true':
            if response['response']['group']:
                return self.connection.output(response['response']['group'])
            else:
                return None
        else:
            return None
