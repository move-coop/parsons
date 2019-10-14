"""NGPVAN Changed Entities"""

from parsons.etl.table import Table
import logging

logger = logging.getLogger(__name__)


class ChangedEntities(object):

    def __init__(self):

        pass

    def get_changed_entity_resources(self):
        """
        Get changed entity resources available to the API user.

        `Returns:`
            list
        """

        r = self.connection.get_request(f'changedEntityExportJobs/resources')
        logger.info(f'Found {len(r)} changed entity resources.')
        return r

    def get_changed_entity_resource_fields(self, resource_type):
        """
        Get export fields avaliable for each changed entity resource.

        `Args:`
            resource_type: str
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = Table(self.connection.get_request(f'changedEntityExportJobs/fields/{resource_type}'))
        logger.info(f'Found {tbl.num_rows} fields for {resource_type}.')
        return tbl
