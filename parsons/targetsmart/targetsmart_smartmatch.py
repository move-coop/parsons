"""Implements client routine to allow execution of TargetSmart SmartMatch
workflows.

TargetSmart SmartMatch API doc:
https://docs.targetsmart.com/developers/tsapis/v2/service/smartmatch.html
"""

import gzip
import logging
import shutil
import tempfile
import time
import uuid

import petl
import requests

from parsons import Table

logger = logging.getLogger(__name__)

VALID_FIELDS = [
    "voterbase_id",
    "smartvan_id",
    "voter_id",
    "exact_track",
    "full_name",
    "first_name_combined",
    "first_name",
    "middle_name",
    "last_name",
    "name_suffix",
    "address1",
    "address2",
    "city",
    "state",
    "zip",
    "age",
    "gender",
    "dob",
    "phone",
    "email",
    "latitude",
    "longitude",
]

INTERNAL_JOIN_ID = "matchback_id"
INTERNAL_JOIN_ID_CONFLICT = "__matchback_id"


class SmartMatchError(Exception):
    """Raised when SmartMatch workflow processing fails."""


def _smartmatch_upload(url, fname):
    logger.info(f"Uploading {fname} to {url} to begin SmartMatch workflow execution.")
    with open(fname, "rb") as reader:
        response_2 = requests.put(url, data=reader, headers={"Content-Type": ""})

    response_2.raise_for_status()


def _smartmatch_download(url, writer):
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=8192):
            writer.write(chunk)


def _add_join_id(input_table):
    """`matchback_id` is added to the raw input table so the results can later be
    joined back. Integer sequence values are used. If the column already exists
    in the raw input, it is renamed to `__matchback_id` and restored after
    result join.
    """
    if INTERNAL_JOIN_ID in input_table.fieldnames():
        input_table = input_table.rename(INTERNAL_JOIN_ID, INTERNAL_JOIN_ID_CONFLICT)

    return input_table.addrownumbers(field=INTERNAL_JOIN_ID)


def _prepare_input(intable, tmpdir):
    valid = VALID_FIELDS + [INTERNAL_JOIN_ID]
    supported = set(intable.fieldnames()) & set(valid)
    if not supported:
        raise SmartMatchError(
            "No supported field identifiers were found in the input table."
            f" Expecting one or more from: {VALID_FIELDS}"
        )
    return intable.cut(*supported)


class SmartMatch:
    """
    Works as a mixin to the TargetSmartAPI class.
    """

    def __init__(self):
        # Set by TargetSmartAPI constructor
        self.connection = None

    def _smartmatch_poll(self, poll_url, submit_filename):
        download_url = None
        while True:
            poll_response = requests.get(
                poll_url,
                {"filename": submit_filename},
                headers=self.connection.headers,
            )

            if poll_response.ok:
                poll_info = poll_response.json()

                if poll_info["error"]:
                    raise SmartMatchError(poll_info["error"])

                download_url = poll_info["url"]
                if download_url:
                    break
            time.sleep(60 * 2.5)
        return download_url

    def smartmatch(
        self,
        input_table,
        max_matches=1,
        include_email=False,
        include_landline=False,
        include_wireless=False,
        include_voip=False,
        tmp_location=None,
        keep_smartmatch_input_file=False,
        keep_smartmatch_output_gz_file=False,
    ):
        """Submit the contact list records available in the Parsons table ``input_table`` to
        TargetSmart SmartMatch.

        * `SmartMatch overview <https://docs.targetsmart.com/my_tsmart/smartmatch/overview.html>`_
        * `SmartMatch API doc <https://docs.targetsmart.com/developers/tsapis/v2/service/smartmatch.html>`_
        * `Supported input header field identifiers <https://docs.targetsmart.com/developers/tsapis/v2/service/smartmatch.html#supported-field-identifiers>`_

        Your application provides a contact list which will be matched to
        TargetSmart’s database of voting age individuals.

        `TargetSmart Client Services <mailto:support@targetsmart.com>`_
        provisions SmartMatch for your API key, configuring the fields from the
        TargetSmart Data Dictionary that will be appended to each matched
        record.

        This method blocks until TargetSmart has completed the remote workflow
        execution. The execution time can take minutes to hours to complete
        depending on the file size, the types of field identifiers present, and
        TargetSmart system load. SmartMatch executions cannot be canceled once
        submitted to TargetSmart.

        Since Parsons Petl tables are lazy, the SmartMatch output file is always
        retained in ``tmp_location``. If your Parsons-based ETL workflow fails
        downstream it may be beneficial to recover the raw SmartMatch output
        from this location. You may delete this data when it is no longer
        needed.

        `Args:`
            input_table: Parsons or Petl table
                A Parsons table with `header field names supported by SmartMatch <https://docs.targetsmart.com/developers/tsapis/v2/service/smartmatch.html#supported-field-identifiers>`_. Required.
            max_matches: int
                By default only a single best match is returned for an input record. Increase to return additional potentially accurate matches for each input record. Value between 1-10. Default of 1.
            include_email: bool
                Set to True to include appended email values for matched records. This is only applicable if your TargetSmart account is configued to return email data. Additional charges may apply if True. Default of False.
            include_landline: bool
                Set to True to include appended landline phone number values for matched records. This is only applicable if your TargetSmart account is configued to return landline phone data. Additional charges may apply if True. Default of False.
            include_wireless: bool
                Set to True to include appended wireless phone number values for matched records. This is only applicable if your TargetSmart account is configued to return wireless phone data. Additional charges may apply if True. Default of False.
            include_voip: bool
                Set to True to include appended VOIP phone number values for matched records. This is only applicable if your TargetSmart account is configued to return VOIP phone data. Additional charges may apply if True. Default of False.
            tmp_location: str
                Optionally provide a local directory path where input/output CSV files will be stored. Useful to recover CSV output if downstream ETL processing fails. If not specified, a system tmp location is used. Default of None.
            keep_smartmatch_input_file: bool
                Optionally keep the CSV input file that is uploaded in ``tmp_location`` for later use. Default of False.
            keep_smartmatch_output_gz_file: bool
                Optionally keep the gzip compressed output file in ``tmp_location`` for later use. The uncompressed output file is always retained in ``tmp_location``. Default of False
        `Returns:`
            Parsons Table
                A Parsons table wrapping the SmartMatch execution output file records. Each record will
                include the input record fields followed by columns named ``tsmart_match_code``, a
                match indicator, ``vb.voterbase_id``, and zero or more additional data
                element fields based on your TargetSmart account configuration.
                See :ref:`parsons-table` for output options.
        """  # noqa

        # If `input_table` is a Parsons table, convert it to a Petl table.
        if hasattr(input_table, "table"):
            input_table = input_table.table

        url = self.connection.uri + "service/smartmatch"
        poll_url = f"{url}/poll"

        if not input_table:
            raise ValueError(
                "Missing `input_table`. A Petl table must be provided with" " valid input rows."
            )

        if not hasattr(input_table, "tocsv"):
            raise ValueError("`input_table` isn't a valid table.")

        if int(max_matches) > 10:
            raise ValueError("max_matches cannot be greater than 10")

        if not tmp_location:
            tmp_location = tempfile.mkdtemp()

        logger.info("Preparing data for SmartMatch submission.")
        input_table = _add_join_id(input_table)
        dataprep_table = _prepare_input(input_table, tmp_location)
        # Unique execution label for each submission
        submit_filename = f"tmc_{str(uuid.uuid4())[0:10]}.csv"

        # An initial api.targetsmart.com request is performed to register the
        # job execution. The response returns a presigned S3 url where data
        # records will be uploaded.
        response_1 = requests.get(
            url,
            {
                "filename": submit_filename,
                "include_email": include_email,
                "include_landline": include_landline,
                "include_wireless": include_wireless,
                "include_voip": include_voip,
                "max_matches": max_matches,
                "format": "gzip",
            },
            headers=self.connection.headers,
        )
        response_1.raise_for_status()
        response_1_info = response_1.json()
        if response_1_info["error"]:
            raise SmartMatchError(
                "SmartMatch workflow registration failed. Error:" f" {response_1_info['error']}"
            )

        logger.info(
            "The SmartMatch workflow registration was successful for file name"
            f" {submit_filename}."
        )

        # Write Petl table to CSV and upload for SmartMatch to process
        with tempfile.NamedTemporaryFile(
            mode="w+",
            encoding="utf8",
            newline="\n",
            prefix="smartmatch_input",
            suffix=".csv",
            dir=tmp_location,
            delete=not keep_smartmatch_input_file,
        ) as tmp:
            dataprep_table.tocsv(tmp.name, encoding="utf8")
            tmp.flush()
            _smartmatch_upload(response_1_info["url"], tmp.name)

        logger.info(
            "The SmartMatch workflow execution has been submitted using file"
            f" name '{submit_filename}'. Now polling for results which can take"
            " minutes/hours depending on data size and queuing."
        )

        # Poll SmartMatch endpoint waiting for workflow completion
        download_url = self._smartmatch_poll(poll_url, submit_filename)

        # Download SmartMatch .csv.gz results, decompress, and Petl table wrap.
        # The final tmp file cannot be deleted due to Petl tables being lazy.
        with tempfile.NamedTemporaryFile(
            prefix="smartmatch_output",
            suffix=".csv.gz",
            dir=tmp_location,
            delete=not keep_smartmatch_output_gz_file,
        ) as tmp_gz:
            with tempfile.NamedTemporaryFile(
                prefix="smartmatch_output",
                suffix=".csv",
                dir=tmp_location,
                delete=False,
            ) as tmp_csv:
                logger.info(
                    f"Downloading the '{submit_filename}' SmartMatch results to" f" {tmp_gz.name}."
                )
                _smartmatch_download(download_url, tmp_gz)
                tmp_gz.flush()

                logger.info("Decompressing results")
                with gzip.open(tmp_gz.name, "rb") as gz_reader:
                    shutil.copyfileobj(gz_reader, tmp_csv)
                tmp_csv.flush()

                raw_outtable = petl.fromcsv(  # pylint: disable=no-member
                    tmp_csv.name, encoding="utf8"
                ).convert(INTERNAL_JOIN_ID, int)
                logger.info(
                    "SmartMatch remote execution successful. Joining results to" " input table."
                )
                outtable = (
                    petl.leftjoin(  # pylint: disable=no-member
                        input_table,
                        raw_outtable,
                        key=INTERNAL_JOIN_ID,
                        tempdir=tmp_location,
                    )
                    .sort(key=INTERNAL_JOIN_ID)
                    .cutout(INTERNAL_JOIN_ID)
                )
                if INTERNAL_JOIN_ID_CONFLICT in input_table.fieldnames():
                    input_table = input_table.rename(INTERNAL_JOIN_ID_CONFLICT, INTERNAL_JOIN_ID)

                return Table(outtable)
