"""NGPVAN Target Endpoints"""

from parsons.etl.table import Table
import logging
import petl

logger = logging.getLogger(__name__)


class TargetsFailed(Exception):
    pass


class Targets(object):
    def __init__(self, van_connection):

        self.connection = van_connection

    def obj_dict(obj):
        return obj.__dict__

    def get_targets(self):
        """
        Get targets.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = Table(self.connection.get_request("targets"))
        logger.info(f"Found {tbl.num_rows} targets.")
        return tbl

    def get_target(self, target_id):
        """
        Get a single target.

        `Args:`
            target_id : int
                The target id.
        `Returns:`
            dict
                The target
        """

        r = self.connection.get_request(f"targets/{target_id}")
        logger.info(f"Found target {target_id}.")
        return r

    def get_target_export(self, export_job_id):
        """
        Get specific target export job id's status.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        response = self.connection.get_request(f"targetExportJobs/{export_job_id}")
        job_status = response.get("jobStatus")
        if job_status == "Complete":
            url = response["file"]["downloadUrl"]
            return Table(petl.fromcsv(url, encoding="utf-8-sig"))
        elif job_status == "Pending" or job_status == "InProcess":
            logger.info(f"Target export job is pending or in process for {export_job_id}.")
        else:
            raise TargetsFailed(f"Target export failed for {export_job_id}")

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
        target_export = {"targetId": target_id}

        r = self.connection.post_request("targetExportJobs", json=target_export)
        logger.info(f"Created new target export job for {target_id}.")
        return r
