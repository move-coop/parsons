import errno
import gzip
import os
import shutil
import tempfile

__all__ = [
    "create_temp_file",
    "create_temp_file_for_path",
    "is_gzip_path",
    "suffix_for_compression_type",
    "compression_type_for_path",
    "string_to_temp_file",
]


# Maximum number of times to try to open a new temp file before giving up.
TMP_MAX = 1000


# This global list keeps track of all temp files created during the runtime of a script.
# We can't rely exclusively on the "automatic removal" behavior of the built-in `tempfile`
# library, because of our use of petl. Specifically, if a petl table is loaded from a
# temporary file (eg. a CSV), petl may not actually read the file until much later, after the
# TemporaryFile object has already gone out of scope and the file removed. If this
# occurs, the petl load will fail since it's trying to read from a file that doesn't exist.
# So by storing all the temp files in this list, we can keep them "in scope" for the remaining
# runtime of the script.
_temp_files = []

# Same as above, but for our temp directories.
_temp_directories = []


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
    temp_file = TempFile(suffix=suffix)
    _temp_files.append(temp_file)
    return temp_file.name


def create_temp_directory():
    """
    Create a temp directory that will exist as long as the current script is running.

    `Returns:`
        str
            The path of the temp directory
    """
    temp_dir = TempDirectory()
    _temp_directories.append(temp_dir)
    return temp_dir.name


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
    suffix = ".gz" if is_gzip_path(path) else None
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
            # Call remove explicitly to clean up, because we can't always assume that de-refencing
            # will necessarily result in the TempFile being cleaned up (depends on platform)
            temp_file.remove()
            _temp_files.remove(temp_file)
            return True

    return False


def cleanup_temp_directory(path):
    """
    Force closes a Parsons temp directory, which will cause it and its files to be deleted.

    Useful for when you don't want to wait until the end of your script's execution for temp
    files to be closed and deleted. Eg. If you're running into system limits on open file
    descriptors.

    `Args:`
        path: str
            Path of a temp directory created by ``create_temp_directory``
    `Returns:`
        bool
            Whether the temp directory was found and closed
    """

    for temp_dir in _temp_directories:
        if temp_dir.name == path:
            # Call remove explicitly to clean up, because we can't always assume that de-refencing
            # will necessarily result in the TempDirectory being cleaned up (depends on platform)
            temp_dir.remove()
            _temp_directories.remove(temp_dir)
            return True

    return False


def track_temp_file(path):
    """
    Start tracking a file as a "temp" file that needs to be cleaned up by Parsons.


    `Args:`
        path: str
            The path of the file to start tracking
    `Returns:`
        str
            The path of the file to start tracking
    """
    temp_file = TempFile(path)
    _temp_files.append(temp_file)
    return path


def is_gzip_path(path):
    return path[-3:] == ".gz"


def is_zip_path(path):
    return path[-4:] == ".zip"


def is_csv_path(path):
    return path[-4:].lower() == ".csv"


def suffix_for_compression_type(compression):
    if compression == "gzip":
        return ".gz"

    return ""


def compression_type_for_path(path):
    if is_gzip_path(path):
        return "gzip"

    if is_zip_path(path):
        return "zip"

    return None


def valid_table_suffix(path):
    # Checks if the suffix is valid for conversions to a Parsons table.

    if is_csv_path(path) or is_gzip_path(path) or is_zip_path(path):
        return True
    else:
        return False


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
        "gzip": gzip.open,
        None: open,
    }
    with open_func[compression](path, "r") as fp:
        return fp.read()


def string_to_temp_file(string, suffix=None):
    """
    Create a temporary file from a string. Currently used for packages
    that require credentials to be stored as a file.
    """

    temp_file_path = create_temp_file(suffix=suffix)

    with open(temp_file_path, "w") as f:
        f.write(string)

    return temp_file_path


def zip_check(file_path, compression_type):
    """
    Check if the file suffix or the compression type indicates that it is
    a zip file.
    """

    if file_path:
        if file_path.split("/")[-1].split(".")[-1] == "zip":
            return True

    if compression_type == "zip":
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
        return file_path.split("/")[-1]

    return file_path.split("/")[-1].split(".")[0]


def has_data(file_path):
    """
    Check if a file has any data in it.

    `Args:`
        file_path: str
            The file path.
    `Returns:`
        boolean
            ``True`` if data in the file and ``False`` if not.
    """

    if os.stat(file_path).st_size == 0:
        return False

    else:
        return True


def generate_tempfile(suffix=None, create=False):
    """
    Create a new temp file with a unique filename.

    `Args:`
        suffix: str
            The suffix to give the file path in order to advertise the file/mime type of the file.
    `Returns`
        str
            The path of the newly created temp file.
    """
    # _get_candidate_names gives us an iterator that will keep trying to generate a random filename.
    # It's not ideal to use a "protected" function from another module, but this function does some
    # heavy lifting for us.
    names = tempfile._get_candidate_names()
    temp_dir = tempfile.gettempdir()

    # Try multiple times to create a temp file, just in case (however unlikely) we have some
    # collisions with already existing files.
    for _ in range(TMP_MAX):
        name = next(names)
        if suffix:
            name = f"{name}{suffix}"
        path = os.path.join(temp_dir, name)

        # Check to see if the path already exists.
        if os.path.exists(path):
            continue

        # If we aren't creating it here, then just return the name
        if not create:
            return path

        try:
            # "Touch" the file to ensure that there is a file there, so that if our user tries
            # open it in read mode later, they won't get an error about the file not existing.
            # Also, use mode='x' (exclusive create) to make sure we get an error if the file already
            # exists
            with open(path, mode="x") as _:
                pass
            return path
        # PermissionError can be Windows' way of saying the file exists
        except (FileExistsError, PermissionError):
            continue  # try again with another filename if we got an error

    raise FileExistsError(errno.EEXIST, "No usable temporary directory name found")


class TempDirectory:
    """
    Class for creating and eventually cleaning up a temporary directory.

    Creating the instance of the TempDirectory will create a uniquely named temporary dir. When the
    instance is garbage collected (e.g., when the Python process closes) or when the remove method
    is called explicitly, the temporary directory is removed from disk.

    Creating the instance will also create the directory itself, so files can be loaded immediately.
    """

    def __init__(self, mkdir=os.makedirs):
        self.remove_called = False
        self.name = generate_tempfile()

        mkdir(self.name)

    def __del__(self):
        # When we are being cleaned up, call remove to make sure the file is removed from disk.
        self.remove()

    def remove(self, cleanup=shutil.rmtree):
        """
        Remove the file from disk.

        Note: We cache a reference to the os.unlink function because during shutdown of the Python
        process, the reference to the os module may be None'd out as part of garbage collection.
        So, we want to make sure we have a reference to the function saved somewhere.

        `Args:`
            unlink: function
                Function to use for removing the file from disk.
        """
        # Only try to unlink if we have a valid file path and we haven't yet called close.
        if self.name and not self.remove_called:
            try:
                cleanup(self.name)
            except FileNotFoundError:
                pass  # if the file isn't found, our work is done

        self.remove_called = True


class TempFile:
    """
    Class for creating and eventually cleaning up a temporary file.

    Creating the instance of the TempFile will create a uniquely named temporary file. When the
    instance is garbage collected (e.g., when the Python process closes) or when the remove method
    is called explicitly, the temporary file is removed from disk.

    Unlike NamedTemporaryFile from the Python standard library, this class does NOT represent
    an open file handle to the file. It simply represents a file on disk. This class was
    written to workaround the fact that on Windows, NamedTemporaryFile opens the file with an
    exclusive read lock, which means that no one else can open the file for reading.

    Since Parsons hands out the temporary file's path and not the file handle, users must be able
    to open the file, but that is impossible as long as NamedTemporaryFile holds onto the open
    file handle with its exclusive read lock. So we wrote, TempFile to not hold onto the open
    file handle.

    `Args:`
        suffix: str
            The suffix to give the file path in order to advertise the file/mime type of the file.
    """

    def __init__(self, name=None, suffix=None):
        self.remove_called = False
        self.name = name or generate_tempfile(suffix)

    def __del__(self):
        # When we are being cleaned up, call remove to make sure the file is removed from disk.
        self.remove()

    def remove(self, unlink=os.unlink):
        """
        Remove the file from disk.

        Note: We cache a reference to the os.unlink function because during shutdown of the Python
        process, the reference to the os module may be None'd out as part of garbage collection.
        So, we want to make sure we have a reference to the function saved somewhere.

        `Args:`
            unlink: function
                Function to use for removing the file from disk.
        """
        # Only try to unlink if we have a valid file path and we haven't yet called close.
        if self.name and not self.remove_called:
            try:
                unlink(self.name)
            except FileNotFoundError:
                pass  # if the file isn't found, our work is done

        self.remove_called = True
