

class SupporterGroups(object):
    """Class for '/activistCodes' end points."""

    def __init__(self, van_connection):
        """Initialize class"""

        self.connection = van_connection

    def get_supporter_groups(self):
        """
        Get supporter group objects

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        url = self.connection.uri + 'supporterGroups'

        return self.connection.request_paginate(url)

    def get_supporter_group(self, supporter_group_id):
        """
        Get a single supporter group object

        `Args:`
            supporter_group_id : int
                The activist code id associated with the activist code.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        url = self.connection.uri + \
            'supporterGroups/{}'.format(supporter_group_id)

        return self.connection.request(url)

    def create_supporter_group(self, name, description):
        """
        Create a new supporter group

        `Args:`
            name: str
                The name of the supporter group. 100 character limit
            description: str
                Optional; A description of the supporter group. 200 character limit.
        `Returns`
            Parsons Table with the newly createed supporter group id, name
            and description
        """

        url = self.connection.uri + 'supporterGroups'

        json = {'name': name, 'description': description}

        return self.connection.request(url, req_type="POST", post_data=json)

    def add_person_supporter_group(self, supporter_group_id, vanid):
        """
        Add a person to a supporter group

        `Args:`
            supporter_group_id: int
                The supporter group id
            vanid: int
                The vanid of the person to apply
        """

        url = self.connection.uri + \
            'supporterGroups/{}/people/{}'.format(supporter_group_id, vanid)

        return self.connection.request(url, req_type="PUT")

    def delete_person_supporter_group(self, supporter_group_id, vanid):
        """
        Remove a person from a supporter group

        `Args:`
            supporter_group_id: int
                The supporter group id
            vanid: int
                The vanid of the person to remove
        """

        url = self.connection.uri + \
            'supporterGroups/{}/people/{}'.format(supporter_group_id, vanid)

        return self.connection.request(url, req_type="DELETE")
