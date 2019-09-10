import zipfile


def create_archive(archive_path, file_path, file_name=None, if_exists='replace'):
    """
    `Args:`
        archive_name: str
            The file name of zip archive
        csv_path: str
            The path of the file
        if_exists: str
            If archive already exists, one of 'replace' or 'append'
    `Returns:`
        Zip archive path
    """

    if if_exists == 'append':
        write_type = 'a'
    else:
        write_type = 'w'

    if not file_name:
        file_name = file_path.split('/')[-1]

    with zipfile.ZipFile(archive_path, write_type) as z:
        z.write(file_path, arcname=file_name, compress_type=zipfile.ZIP_STORED)

    return archive_path
