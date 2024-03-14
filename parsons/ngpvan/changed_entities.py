"""NGPVAN Changed Entities"""

from parsons.etl.table import Table
import logging
import time

logger = logging.getLogger(__name__)

RETRY_RATE = 10


class ChangedEntities(object):
    def __init__(self):

        pass

    def get_changed_entity_resources(self):
        """
        Get changed entity resources available to the API user.

        `Returns:`
            list
        """

        r = self.connection.get_request("changedEntityExportJobs/resources")
        logger.info(f"Found {len(r)} changed entity resources.")
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

        tbl = Table(self.connection.get_request(f"changedEntityExportJobs/fields/{resource_type}"))
        logger.info(f"Found {tbl.num_rows} fields for {resource_type}.")
        return tbl

    def get_changed_entities(
        self,
        resource_type,
        date_from,
        date_to=None,
        include_inactive=False,
        requested_fields=None,
        custom_fields=None,
    ):
        """
        Get modified records for VAN from up to 90 days in the past.

        `Args:`
            resource_type: str
                The type of resource to export. Use the :py:meth:`~parsons.ngpvan.changed_entities.ChangedEntities.get_changed_entity_resources`
                to get a list of potential entities.
            date_from: str
                The start date in which to search. Must be less than 90 days in the
                past. Must be``iso8601`` formatted date (``2021-10-11``).
            date_to: str
                The end date to search. Must be less than 90 days in the
                past. Must be``iso8601`` formatted date (``2021-10-11``).
            include_inactive: boolean
                Include inactive records
            requested_fields: list
                A list of optional requested fields to include. These options can be accessed through
                :py:meth:`~parsons.ngpvan.changed_entities.ChangedEntities.get_changed_entity_resource_fields`
                method.
            custom_fields: list
                A list of ids of custom fields to include in the export.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """  # noqa: E501

        json = {
            "dateChangedFrom": date_from,
            "dateChangedTo": date_to,
            "resourceType": resource_type,
            "requestedFields": requested_fields,
            "requestedCustomFieldIds": custom_fields,
            "fileSizeKbLimit": 100000,
            "includeInactive": include_inactive,
        }

        r = self.connection.post_request("changedEntityExportJobs", json=json)

        while True:
            status = self._get_changed_entity_job(r["exportJobId"])
            if status["jobStatus"] in ["Pending", "InProcess"]:
                logger.info("Waiting on export file.")
                time.sleep(RETRY_RATE)
            elif status["jobStatus"] == "Complete":
                return Table.from_csv(status["files"][0]["downloadUrl"])
            else:
                raise ValueError(status["message"])

    def _get_changed_entity_job(self, job_id):

        r = self.connection.get_request(f"changedEntityExportJobs/{job_id}")
        return r
