"""NGPVAN Target Endpoints"""

from parsons.etl.table import Table
from parsons.ngpvan.utilities import action_parse
import logging

logger = logging.getLogger(__name__)


class TargetExport(object):

    def __init__(self, van_connection):

        self.connection = van_connection

    def get_target_export(self, export_job_id):
        """
        Get specific target export job id's status.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = Table(self.connection.get_request(f'targetExportJobs/{export_job_id}'))
        logger.info(f'Found target export {export_job_id}.')
        return tbl


    def create_target_export(self, target_id, webhook_url=None):
        """
        Create new target export job

        `Args:`
            target_id : int
                The target id the export job is creating for.
        `Returns:`
            dict
                The target export job ID
        """
        target_export = {
                        'target_id' : target_id
                        }

        r = self.connection.post_request(f'targetExportJobs', json=target_export)
        logger.info(f'Created new target export job for {target_id}.')
        return r

