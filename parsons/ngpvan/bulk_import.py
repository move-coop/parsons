"""NGPVAN Bulk Import Endpoints"""

import logging
logger = logging.getLogger(__name__)


class BulkImport(object):

    def __init__(self):

        pass

    def get_bulk_import_resources(self):
        """
        Get bulk import resources that available to the user. These define
        the types of bulk imports that you can run. These might include
        ``Contacts``, ``ActivistCodes``, ``ContactsActivistCodes`` and others.

        `Returns:`
            list
                A list of resources.
        """

        r = self.connection.get_request(f'bulkImportJobs/resources')
        logger.info(f'Found {len(r)} bulk import resources.')
        return r
