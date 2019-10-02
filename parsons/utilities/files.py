from tempfile import NamedTemporaryFile
import gzip

__all__ = [
    'create_temp_file',
    'create_temp_file_for_path',
    'is_gzip_path',
    'suffix_for_compression_type',
    'compression_type_for_path',
    'string_to_temp_file'
    ]


# This global list keeps track of all temp files created during the runtime of a script.
# We can't rely exclusively on the "automatic removal" behavior of the built-in `tempfile`
# library, because of our use of petl. Specifically, if a petl table is loaded from a
# temporary file (eg. a CSV), petl may not actually read the file until much later, after the
# TemporaryFile object has already gone out of scope and the file removed. If this
# occurs, the petl load will fail since it's trying to read from a file that doesn't exist.
# So by storing all the temp files in this list, we can keep them "in scope" for the remaining
# runtime of the script.
_temp_files = []


def create_temp_file(suffix=None):
    """
    Create a temp file that will exist as long as the current script is running.

    `Args:`
        suffix: str
            A suffix/extension to add to the end of the temp file name
    `Returns:`
        str
            The path of the temp file
    """
    temp_file = NamedTemporaryFile(suffix=suffix)
    _temp_files.append(temp_file)
    return temp_file.name


def create_temp_file_for_path(path):
    """
    Creates a temp file that will exist as long as the current script is running, and with
    a file name mimicking that of the provided path.

    `Args:`
        path: str
            Path (or just file name) of the file you want the temp file to mimick.
    `Returns:`
        str
            The path of the temp file
    """

    # Add the appropriate compression suffix to the file, so other libraries that check the
    # file's extension will know that it is compressed.
    # TODO Make this more robust, maybe even using the entire remote file name as the suffix.
    suffix = '.gz' if is_gzip_path(path) else None
    return create_temp_file(suffix=suffix)


def close_temp_file(path):
    """
    Force closes a Parsons temp file, which will cause it to be deleted immediately.

    Useful for when you don't want to wait until the end of your script's execution for temp
    files to be closed and deleted. Eg. If you're running into system limits on open file
    descriptors.

    `Args:`
        path: str
            Path of a temp file created by ``create_temp_file``
    `Returns:`
        bool
            Whether the temp file was found and closed
    """

    for temp_file in _temp_files:
        if temp_file.name == path:
            _temp_files.remove(temp_file)
            return True

    return False


def is_gzip_path(path):
    return (path[-3:] == '.gz')


def is_zip_path(path):
    return (path[-4:] == '.zip')


def suffix_for_compression_type(compression):
    if compression == 'gzip':
        return '.gz'

    return ''


def compression_type_for_path(path):
    if is_gzip_path(path):
        return 'gzip'

    if is_zip_path(path):
        return 'zip'

    return None


def read_file(path):
    """
    Return the contents of file. Currently support `.gz` compressed files.

    `Args:`
        path: str
            The path to the file to read.
    `Returns:`
        str
            The contents of a files.
    """
    compression = compression_type_for_path(path)

    open_func = {
        'gzip': gzip.open,
        None: open,
    }
    with open_func[compression](path, 'r') as fp:
        return fp.read()


def string_to_temp_file(string, suffix=None):
    """
    Create a temporary file from a string. Currently used for packages
    that require credentials to be stored as a file.
    """

    temp_file_path = create_temp_file(suffix=suffix)

    with open(temp_file_path, 'w') as f:
        f.write(string)

    return temp_file_path


def zip_check(file_path, compression_type):
    """
    Check if the file suffix or the compression type indicates that it is
    a zip file.
    """

    if file_path:
        if file_path.split('/')[-1].split('.')[-1] == 'zip':
            return True

    if compression_type == 'zip':
        return True

    else:
        return False


def extract_file_name(file_path=None, include_suffix=True):
    """
    Extract the file name with the file path string.

    file_path: str
        The file path
    include_suffix: boolean
        If True, includes full file name with suffix. If False returns the
        file name without the suffix (e.g. "myfile.zip" vs. "myfile").
    """

    if not file_path:
        return None

    if include_suffix:
        return file_path.split('/')[-1]

    return file_path.split('/')[-1].split('.')[0]
