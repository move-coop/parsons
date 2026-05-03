import csv
from typing import Literal

from parsons import Table

"""
Generalizable module for moving files to an online file storage class.

It is used by processes that require access to a file via a public url (e.g. VAN).
Currently only includes Amazon S3 and Google Cloud Storage.
"""


def post_file(
    tbl: Table,
    type: Literal["S3", "GCS"],
    file_path: str | None = None,
    quoting: int = csv.QUOTE_MINIMAL,
    **file_storage_args,
) -> str | None:
    """
    This utility function is a generalizable way of moving files
    to an online file storage class.

    It is used by processes that require access to a file via a public url (e.g. VAN).

    Args:
        tbl: Data to post to online file storage.
        type: ``S3`` or ``GCS`` (Google Cloud Storage)
        file_path:
            The file path to store the file.
            Not required if provided with the `**file_storage_args`.
        quoting: The type of quoting to use for the csv.
        `**file_storage_args`: Optional arguments specific to the file storage.

    Raises:
        ValueError: If the type is not ``S3`` or ``GCS``.

    """
    if type.upper() == "S3":
        # Overwrite the file_path if key is passed
        if "key" in file_storage_args:
            file_storage_args["key"] = file_path

        return tbl.to_s3_csv(public_url=True, key=file_path, quoting=quoting, **file_storage_args)

    if type.upper() == "GCS":
        return tbl.to_gcs_csv(
            public_url=True, blob_name=file_path, quoting=quoting, **file_storage_args
        )

    raise ValueError("Type must be S3 or GCS.")
