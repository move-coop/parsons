import zipfile
from pathlib import Path
from typing import Literal

from parsons.utilities.files import create_temp_directory


def create_archive(
    archive_path: Path | str,
    file_path: str,
    file_name: str | None = None,
    if_exists: Literal["replace", "append"] = "replace",
) -> str:
    """
    Create and fill an archive.

    Args:
        archive_path: The file name of zip archive
        file_path: The path of the file
        file_name: The name of the file in the archive
        if_exists: If archive already exists, one of 'replace' or 'append'

    Returns:
        Zip archive path

    """

    write_type: Literal["r", "w", "x", "a"] = "a" if if_exists == "append" else "w"

    if not file_name:
        file_name = file_path.split("/")[-1]

    with zipfile.ZipFile(archive_path, write_type) as z:
        z.write(file_path, arcname=file_name, compress_type=zipfile.ZIP_STORED)

    return str(archive_path)


def unzip_archive(archive_path: Path | str, destination: str | None = None) -> str:
    """
    Unzip an archive.

    Only returns the path of the first file in the archive.

    Args:
        archive_path: Path to the ZIP archive
        destination:
            Path to unzip the archive into
            If not specified, the archive will be unzipped into a temporary directory.

    Returns:
        Extracted file path.

    """
    destination = destination or create_temp_directory()

    with zipfile.ZipFile(archive_path, "r") as z:
        file_name = z.namelist()[0]
        z.extractall(path=destination)

    return str(Path(destination) / file_name)
