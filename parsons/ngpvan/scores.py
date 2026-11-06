"""NGPVAN Score Endpoints"""

import logging
import uuid
from typing import Literal

import petl

from parsons.etl.table import Table
from parsons.utilities import cloud_storage

logger = logging.getLogger(__name__)


class Scores:
    def __init__(self, van_connection):
        self.connection = van_connection

    def get_scores(self):
        """
        Get all scores.

        Returns:
            Table
                See :ref:`Table` for output options.

        """
        tbl = Table(self.connection.get_request("scores"))
        logger.info("Found %s scores.", tbl.num_rows)
        return tbl

    def get_score(self, score_id):
        """
        Get an individual score.

        Args:
            score_id: int
                The score id
        Returns:
            dict

        """
        r = self.connection.get_request(f"scores/{score_id}")
        logger.info("Found score %s.", score_id)
        return r

    def get_score_updates(self, created_before=None, created_after=None, score_id=None):
        """
        Get score updates.

        Args:
            created_before: str
                Filter score updates to those created before date. Use "YYYY-MM-DD"
                format.
            created_after: str
                Filter score updates to those created after date. Use "YYYY-MM-DD"
                format.

        Returns:
            Table
                See :ref:`Table` for output options.

        """
        params = {
            "createdBefore": created_before,
            "createdAfter": created_after,
            "scoreId": score_id,
        }

        tbl = Table(self.connection.get_request("scoreUpdates", params=params))
        if tbl.num_rows:
            tbl.unpack_dict("updateStatistics", prepend=False)
            tbl.unpack_dict("score", prepend=False)
        logger.info("Found %s score updates.", tbl.num_rows)
        return tbl

    def get_score_update(self, score_update_id):
        """
        Get a score update object

        Args:
            score_update_id : int
                The score update id

        Returns:
            dict

        """
        r = self.connection.get_request(f"scoreUpdates/{score_update_id}")
        logger.info("Returning score update %s.", score_update_id)
        return r

    def update_score_status(
        self, score_update_id, status: Literal["pending approval", "approved", "disapproved"]
    ):
        """
        Change the status of a score update object. This end point is used to
        approve a score loading job.

        Args:
            score_update_id: str
                The score update id
            status: str
                One of 'pending approval', 'approved', 'disapproved'

        """
        if status not in ["pending approval", "approved", "disapproved", "canceled"]:
            raise ValueError(
                """Valid inputs for status are, 'pending approval','approved','disapproved','canceled'"""
            )

        else:
            status = "PendingApproval" if status == "pending approval" else status.capitalize()

        json = {"loadStatus": status}

        r = self.connection.patch_request(f"scoreUpdates/{score_update_id}", json=json)
        logger.info("Score %s status updated to %s.", score_update_id, status)
        return r

    def upload_scores(
        self,
        tbl,
        config,
        url_type,
        id_type="vanid",
        email=None,
        auto_approve=True,
        approve_tolerance=0.1,
        **url_kwargs,
    ):
        """
        Upload scores. Use to create or overwrite scores. Multiple score loads
        should be configured in a single call. [1]_

        Args:
            tbl: Table
                A parsons.Table object. The table must contain the scores and first column in the
                table must contain the primary key (e.g. vanid).
            config: list
                The score configuration. A list of dictionaries in which you specify the following

                .. list-table::
                    :widths: 20 80
                    :header-rows: 0

                    * - ``score_column``
                      - The name of the column where the score is housed.
                    * - ``score_id``
                      - The score slot id.

                Example:

                .. code-block:: python

                    [
                        {'score1_id': int, score1_column': str},
                        {'score2_id': int, score2_column': str}
                    ]

            url_type: str
                The cloud file storage to use to post the file (``S3`` or ``GCS``).
                See :ref:`google/cloud_storage:Cloud Storage` for more details.
            email: str
                An email address to send job load status updates.
            auto_approve: bool
                If the scores are within the expected tolerance of deviation from the
                average values provided, then score will be automatically approved.
            approve_tolderance: float
                The deviation from the average scores allowed in order to automatically
                approve the score. Maximum of .1.
            `**url_kwargs`: kwargs
                Arguments to configure your cloud storage url type. See
                :ref:`google/cloud_storage:Cloud Storage` for more details.

        Returns:
            int
               The score load job id.

        .. [1] NGPVAN asks that you load multiple scores in a single call to reduce the load
           on their servers.

        """  # Move to cloud storage
        file_name = str(uuid.uuid1())
        url = cloud_storage.post_file(tbl, url_type, file_path=file_name + ".zip", **url_kwargs)
        logger.info("Table uploaded to %s.", url_type)

        # Generate shell request
        json = {
            "description": "A description",
            "file": {
                "columnDelimiter": "csv",
                "columns": [{"name": c} for c in tbl.columns],
                "fileName": file_name + ".csv",
                "hasHeader": "True",
                "hasQuotes": "False",
                "sourceUrl": url,
            },
            "actions": [],
        }

        # Configure each score
        for i in config:
            action = {
                "actionType": "score",
                "personIdColumn": tbl.columns[0],
                "personIdType": id_type,
                "scoreColumn": i["score_column"],
                "scoreId": i["score_id"],
            }

            if auto_approve:
                average = petl.stats(tbl.table, i["score_column"]).mean
                action["approvalCriteria"] = {
                    "average": average,
                    "tolerance": approve_tolerance,
                }

            json["actions"].append(action)

        # Add email listener
        if email:
            json["listeners"] = [{"type": "EMAIL", "value": email}]

        # Upload scores
        r = self.connection.post_request("fileLoadingJobs", json=json)
        logger.info("Scores job %s created.", r["jobId"])
        return r["jobId"]


class FileLoadingJobs:
    def __init__(self) -> None:
        """
        Initialize the FileLoadingJobs class.

        .. version-removed:: v8.0.0

        """

    def create_file_load(self) -> None:
        """
        Load a file.

        .. version-deprecated:: v0.7.0

            Deprecated in favor of :meth:`~parsons.ngpvan.scores.Scores.upload_scores`.

        .. version-removed:: v8.0.0

        """

    def create_file_load_multi(self) -> None:
        """
        Load multiple scores at the same time.

        .. version-deprecated:: v0.7.0

            Deprecated in favor of :meth:`~parsons.ngpvan.scores.Scores.upload_scores`.

        .. version-removed:: v8.0.0

        """
