import csv
from typing import Literal

from parsons import Table

"""
This utility method is a generalizable method for moving files to an
online file storage class. It is used by methods that require access
to a file via a public url (e.g. VAN). Currently only includes Amazon S3 and
Google Cloud Storage.
"""


def post_file(
    tbl: Table,
    type: Literal["S3", "GCS"],
    file_path=None,
    quoting: int = csv.QUOTE_MINIMAL,
    **file_storage_args,
):
    """
    Move files to an online file storage class.

    Used by methods that require access to a file via a public url (e.g. VAN).

    **S3 is the only option allowed.**

    Args:
        tbl (Table)
        type (Literal["S3", "GCS"])
        file_path (str, optional): The file path to store the file. Not required if provided via
            ``**file_storage_args``. Defaults to None.
        quoting (int, optional): The type of quoting to use for the csv. Defaults to csv.QUOTE_MINIMAL.
        **file_storage_args: Kwargs Optional arguments specific to the file storage.

    """
    if type.upper() == "S3":
        # Overwrite the file_path if key is passed
        if "key" in file_storage_args:
            file_storage_args["key"] = file_path

        return tbl.to_s3_csv(public_url=True, key=file_path, quoting=quoting, **file_storage_args)

    elif type.upper() == "GCS":
        return tbl.to_gcs_csv(
            public_url=True, blob_name=file_path, quoting=quoting, **file_storage_args
        )

    else:
        raise ValueError("Type must be S3 or GCS.")
