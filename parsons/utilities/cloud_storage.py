
"""
This utility method is a generalizable method for moving files to an
online file storage class. It is used by methods that require access
to a file via a public url (e.g. VAN). Currently only includes S3, but
in the future, might include SFTP, and Google Cloud Storage.
"""


def post_file(tbl, type, file_path=None, **file_storage_args):
    """
    `Args:`
        tbl: parsons.Table
            A parsons table object.
        file_path: str
            The file path to store the file. Not required if provided with
            the **file_storage_args.
        **kwargs: kwargs
                Optional arguments specific to the file storage.
    `Returns:`
        ``None``
    """

    if type.capitalize() == 'S3':

        # Overwrite the file_path if key is passed
        if 'key' in file_storage_args:
            file_storage_args['key'] = file_path

        return tbl.to_s3_csv(public_url=True, key=file_path, **file_storage_args)
