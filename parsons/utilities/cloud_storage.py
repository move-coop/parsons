import csv

"""
This utility method is a generalizable method for moving files to an
online file storage class. It is used by methods that require access
to a file via a public url (e.g. VAN). Currently only includes Amazon S3 and
Google Cloud Storage.
"""


def post_file(tbl, type, file_path=None, quoting=csv.QUOTE_MINIMAL, **file_storage_args):
    """
    This utility method is a generalizable method for moving files to an
    online file storage class. It is used by methods that require access
    to a file via a public url (e.g. VAN).

    **S3 is the only option allowed.**

    `Args:`
        tbl: object
            parsons.Table
        type: str
            ``S3`` or ``GCS`` (Google Cloud Storage)
        file_path: str
            The file path to store the file. Not required if provided with
            the **file_storage_args.
        quoting: attr
            The type of quoting to use for the csv.
        **kwargs: kwargs
                Optional arguments specific to the file storage.
    `Returns:`
        ``None``
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
