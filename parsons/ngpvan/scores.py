"""NGPVAN Score Endpoints"""

from parsons.etl.table import Table
from parsons.utilities import cloud_storage
import uuid
import logging
import petl

logger = logging.getLogger(__name__)


class Scores(object):
    def __init__(self, van_connection):

        self.connection = van_connection

    def get_scores(self):
        """
        Get all scores.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = Table(self.connection.get_request("scores"))
        logger.info(f"Found {tbl.num_rows} scores.")
        return tbl

    def get_score(self, score_id):
        """
        Get an individual score.

        `Args:`
            score_id: int
                The score id
        `Returns:`
            dict
        """

        r = self.connection.get_request(f"scores/{score_id}")
        logger.info(f"Found score {score_id}.")
        return r

    def get_score_updates(self, created_before=None, created_after=None, score_id=None):
        """
        Get score updates.

        `Args:`
            created_before: str
                Filter score updates to those created before date. Use "YYYY-MM-DD"
                format.
            created_after: str
                Filter score updates to those created after date. Use "YYYY-MM-DD"
                format.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
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
        logger.info(f"Found {tbl.num_rows} score updates.")
        return tbl

    def get_score_update(self, score_update_id):
        """
        Get a score update object

            `Args:`
                score_update_id : int
                        The score update id
            `Returns:`
                dict
        """

        r = self.connection.get_request(f"scoreUpdates/{score_update_id}")
        logger.info(f"Returning score update {score_update_id}.")
        return r

    def update_score_status(self, score_update_id, status):
        """
        Change the status of a score update object. This end point is used to
        approve a score loading job.

        `Args:`
            score_update_id: str
                The score update id
            status: str
                One of 'pending approval', 'approved', 'disapproved'
        `Returns:`
            ``None``
        """

        if status not in ["pending approval", "approved", "disapproved", "canceled"]:

            raise ValueError(
                """Valid inputs for status are, 'pending approval',
                             'approved','disapproved','canceled'"""
            )

        else:
            if status == "pending approval":
                status = "PendingApproval"
            else:
                status = status.capitalize()

        json = {"loadStatus": status}

        r = self.connection.patch_request(f"scoreUpdates/{score_update_id}", json=json)
        logger.info(f"Score {score_update_id} status updated to {status}.")
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

        `Args:`
            tbl: object
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

                .. highlight:: python
                .. code-block:: python

                  [{'score1_id' : int, score1_column': str}
                   {'score2_id' : int, score2_column': str}]

            url_type: str
                The cloud file storage to use to post the file (``S3`` or ``GCS``).
                See :ref:`Cloud Storage <cloud-storage>` for more details.
            email: str
                An email address to send job load status updates.
            auto_approve: boolean
                If the scores are within the expected tolerance of deviation from the
                average values provided, then score will be automatically approved.
            approve_tolderance: float
                The deviation from the average scores allowed in order to automatically
                approve the score. Maximum of .1.
            **url_kwargs: kwargs
                Arguments to configure your cloud storage url type. See
                :ref:`Cloud Storage <cloud-storage>` for more details.
        `Returns:`
            int
               The score load job id.

        .. [1] NGPVAN asks that you load multiple scores in a single call to reduce the load
           on their servers.
        """

        # Move to cloud storage
        file_name = str(uuid.uuid1())
        url = cloud_storage.post_file(tbl, url_type, file_path=file_name + ".zip", **url_kwargs)
        logger.info(f"Table uploaded to {url_type}.")

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
        logger.info(f"Scores job {r['jobId']} created.")
        return r["jobId"]


class FileLoadingJobs(object):
    def __init__(self, van_connection):

        self.connection = van_connection

    def create_file_load(
        self,
        file_name,
        file_url,
        columns,
        id_column,
        id_type,
        score_id,
        score_column,
        delimiter="csv",
        header=True,
        quotes=True,
        description=None,
        email=None,
        auto_average=None,
        auto_tolerance=None,
    ):
        """
        .. warning::
           .. deprecated:: 0.7 Use :func:`parsons.VAN.upload_scores` instead.

        Loads a file. Only used for loading scores at this time. Scores must be
        compressed using `zip`.

        `Args:`
            file_name: str
                The name of the file contained in the zip file.
            file_url: str
                The url path to directly download the file. Can also be a path to an FTP site.
            columns: list
                A list of column names contained in the file.
            id_column: str
                The column name of the id column in the file.
            id_type: str
                A valid primary key, such as `VANID` or `DWID`. Varies by VAN instance.
            score_id: int
                The score slot id
            score_column: str
                    The column holding the score
            delimiter: str
                    The file delimiter used.
            email: str
                A valid email address in which file loading status will be sent.
            auto_average: float
                The average of scores to be loaded.
            auto_tolerance: float
                The fault tolerance of the VAN calculated average compared to the ``auto_average``.
                The tolerance must be less than 10% of the difference between the maximum and
                minimum possible acceptable values of the score.
        `Returns:`
            dict
                The file load id
        """

        columns = [{"name": c} for c in columns]

        # To Do: Validate that it is a .zip file. Not entirely sure if this is possible
        # as some urls might not end in ".zip".

        if delimiter not in ["csv", "tab", "pipe"]:
            raise ValueError("Delimiter must be one of 'csv', 'tab' or 'pipe'")

        delimiter = delimiter.capitalize()

        json = {
            "description": "A description",
            "file": {
                "columnDelimiter": delimiter,
                "columns": columns,
                "fileName": file_name,
                "hasHeader": header,
                "hasQuotes": quotes,
                "sourceUrl": file_url,
            },
            "actions": [
                {
                    "actionType": "score",
                    "personIdColumn": id_column,
                    "personIdType": id_type,
                    "scoreColumn": score_column,
                    "scoreId": score_id,
                }
            ],
            "listeners": [{"type": "EMAIL", "value": email}],
        }

        if auto_average and auto_tolerance:

            json["actions"]["approvalCriteria"] = {
                "average": auto_average,
                "tolerance": auto_tolerance,
            }

        r = self.connection.post_request("fileLoadingJobs", json=json)["jobId"]
        logger.info(f"Score loading job {r} created.")
        return r

    def create_file_load_multi(
        self,
        file_name,
        file_url,
        columns,
        id_column,
        id_type,
        score_map,
        delimiter="csv",
        header=True,
        quotes=True,
        description=None,
        email=None,
    ):
        """
        .. warning::
           .. deprecated:: 0.7 Use :func:`parsons.VAN.upload_scores` instead.

        An iteration of the :meth:`file_load` method that allows you to load multiple scores
        at the same time.

        `Args:`
            file_name : str
                The name of the file contained in the zip file.
            file_url : str
                The url path to directly download the file. Can also be a path to an FTP site.
            columns: list
                A list of column names contained in the file.
            id_column : str
                The column name of the id column in the file.
            id_type : str
                A valid primary key, such as `VANID` or `DWID`. Varies by VAN instance.
            score_map : list
                A list of dicts that adheres to the following syntax

                .. highlight:: python
                .. code-block:: python

                    [{'score_id' : int,
                      'score_column': str,
                      'auto_average': float,
                      'auto_tolerance': float }]

            email: str
                A valid email address in which file loading status will be sent.
        `Returns:`
            The file load job id
        """

        columns = [{"name": c} for c in columns]

        # To Do: Validate that it is a .zip file. Not entirely sure if this is possible
        # as some urls might not end in ".zip".

        if delimiter not in ["csv", "tab", "pipe"]:
            raise ValueError("Delimiter must be one of 'csv', 'tab' or 'pipe'")

        delimiter = delimiter.capitalize()

        json = {
            "description": "A description",
            "file": {
                "columnDelimiter": delimiter,
                "columns": columns,
                "fileName": file_name,
                "hasHeader": header,
                "hasQuotes": quotes,
                "sourceUrl": file_url,
            },
            "listeners": [{"type": "EMAIL", "value": email}],
        }

        actions = []

        for score in score_map:

            action = {
                "actionType": "score",
                "personIdColumn": id_column,
                "personIdType": id_type,
                "scoreColumn": score["score_column"],
                "scoreId": score["score_id"],
                "approvalCriteria": {
                    "average": score["auto_average"],
                    "tolerance": score["auto_tolerance"],
                },
            }

            actions.append(action)

        json["actions"] = actions

        r = self.connection.post_request("fileLoadingJobs", json=json)["jobId"]
        logger.info(f"Score loading job {r} created.")
        return r
