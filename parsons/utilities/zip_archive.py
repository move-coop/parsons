import os
import zipfile
from parsons.utilities.files import create_temp_directory


def create_archive(archive_path, file_path, file_name=None, if_exists="replace"):
    """
    Create and fill an archive.

    `Args:`
        archive_path: str
            The file name of zip archive
        file_path: str
            The path of the file
        file_name: str
            The name of the file in the archive
        if_exists: str
            If archive already exists, one of 'replace' or 'append'
    `Returns:`
        Zip archive path
    """

    if if_exists == "append":
        write_type = "a"
    else:
        write_type = "w"

    if not file_name:
        file_name = file_path.split("/")[-1]

    with zipfile.ZipFile(archive_path, write_type) as z:
        z.write(file_path, arcname=file_name, compress_type=zipfile.ZIP_STORED)

    return archive_path


def unzip_archive(archive_path, destination=None):
    """
    Unzip an archive. Only returns the path of the first
    file in the archive.

    `Args:`
        archive_path: str
            Path to the ZIP archive
        destination: str
            `Optional`; path to unzip the archive into; if not specified, the
    `Returns:`
        Extracted file path.
    """
    destination = destination or create_temp_directory()

    with zipfile.ZipFile(archive_path, "r") as z:
        file_name = z.namelist()[0]
        z.extractall(path=destination)
        return os.path.join(destination, file_name)
