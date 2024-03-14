"""NGPVAN Supporter Groups Endpoints"""

from parsons.etl.table import Table
import logging

logger = logging.getLogger(__name__)


class SupporterGroups(object):
    def __init__(self, van_connection):

        self.connection = van_connection

    def get_supporter_groups(self):
        """
        Get supporter groups.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = Table(self.connection.get_request("supporterGroups"))
        logger.info(f"Found {tbl.num_rows} supporter groups.")
        return tbl

    def get_supporter_group(self, supporter_group_id):
        """
        Get a supporter group.

        `Args:`
            supporter_group_id: int
                The supporter group id.
        `Returns:`
            dict
        """

        r = self.connection.get_request(f"supporterGroups/{supporter_group_id}")
        logger.info(f"Found supporter group {supporter_group_id}.")
        return r

    def create_supporter_group(self, name, description):
        """
        Create a new supporter group.

        `Args:`
            name: str
                The name of the supporter group. 100 character limit
            description: str
                Optional; A description of the supporter group. 200 character limit.
        `Returns`
            Parsons Table with the newly createed supporter group id, name
            and description
        """

        json = {"name": name, "description": description}
        r = self.connection.post_request("supporterGroups", json=json)
        return r

    def delete_supporter_group(self, supporter_group_id):
        """
        Delete a supporter group.

        `Args:`
            supporter_group_id: int
                The supporter group id
        `Returns:`
            ``None``
        """

        r = self.connection.delete_request(f"supporterGroups/{supporter_group_id}")
        logger.info(f"Deleted supporter group {supporter_group_id}.")
        return r

    def add_person_supporter_group(self, supporter_group_id, vanid):
        """
        Add a person to a supporter group

        `Args:`
            supporter_group_id: int
                The supporter group id
            vanid: int
                The vanid of the person to apply
        `Returns:`
            ``None``
        """

        r = self.connection.put_request(f"supporterGroups/{supporter_group_id}/people/{vanid}")
        logger.info(f"Added person {vanid} to {supporter_group_id} supporter group.")
        return r

    def delete_person_supporter_group(self, supporter_group_id, vanid):
        """
        Remove a person from a supporter group

        `Args:`
            supporter_group_id: int
                The supporter group id
            vanid: int
                The vanid of the person to remove
        `Returns:`
            ``None``
        """

        r = self.connection.delete_request(f"supporterGroups/{supporter_group_id}/people/{vanid}")
        logger.info(f"Deleted person {vanid} from {supporter_group_id} supporter group.")
        return r
