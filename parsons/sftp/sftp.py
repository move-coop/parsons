import logging
import re
from contextlib import contextmanager
from stat import S_ISDIR, S_ISREG

import paramiko

from parsons.etl import Table
from parsons.sftp.utilities import connect
from parsons.utilities import files as file_utilities

logger = logging.getLogger(__name__)


class SFTP(object):
    """
    Instantiate SFTP Class

    `Args:`
        host: str
            The host name
        username: str
            The user name
        password: str
            The password
        rsa_private_key_file str
            Absolute path to a private RSA key used
            to authenticate stfp connection
        port: int
            Specify if different than the standard port 22
    `Returns:`
        SFTP Class
    """

    def __init__(self, host, username, password, port=22, rsa_private_key_file=None):
        self.host = host
        if not self.host:
            raise ValueError("Missing the SFTP host name")

        self.username = username
        if not self.username:
            raise ValueError("Missing the SFTP username")

        if not (password or rsa_private_key_file):
            raise ValueError("Missing password or SSH authentication key")

        self.password = password
        self.rsa_private_key_file = rsa_private_key_file
        self.port = port

    @contextmanager
    def create_connection(self):
        """
        Create an SFTP connection.

        Returns:
            SFTP Connection object
        """

        transport = paramiko.Transport((self.host, self.port))
        pkey = None
        if self.rsa_private_key_file:
            # we need to read it in
            pkey = paramiko.RSAKey.from_private_key_file(self.rsa_private_key_file)

        transport.connect(username=self.username, password=self.password, pkey=pkey)
        conn = paramiko.SFTPClient.from_transport(transport)
        yield conn
        conn.close()
        transport.close()

    def list_directory(self, remote_path=".", connection=None):
        """
        List the contents of a directory

        `Args:`
            remote_path: str
                The remote path of the directory
            connection: obj
                An SFTP connection object
        `Returns:`
            list of files and subdirectories in the provided directory
        """

        if connection:
            return connection.listdir(path=remote_path)
        else:
            with self.create_connection() as connection:
                return connection.listdir(path=remote_path)

    def make_directory(self, remote_path, connection=None):
        """
        Makes a new directory on the SFTP server

        `Args:`
            remote_path: str
                The remote path of the directory
            connection: obj
                An SFTP connection object
        """

        if connection:
            connection.mkdir(remote_path)
        else:
            with self.create_connection() as connection:
                connection.mkdir(remote_path)

    def remove_directory(self, remote_path, connection=None):
        """
        Remove a directory from the SFTP server

        `Args:`
            remote_path: str
                The remote path of the directory
            connection: obj
                An SFTP connection object
        """

        if connection:
            connection.rmdir(remote_path)
        else:
            with self.create_connection() as connection:
                connection.rmdir(remote_path)

    def get_file(self, remote_path, local_path=None, connection=None):
        """
        Download a file from the SFTP server

        `Args:`
            remote_path: str
                The remote path of the file to download
            local_path: str
                The local path where the file will be downloaded. If not specified, a temporary
                file will be created and returned, and that file will be removed automatically
                when the script is done running.
            connection: obj
                An SFTP connection object
        `Returns:`
            str
                The path of the local file
        """

        if not local_path:
            local_path = file_utilities.create_temp_file_for_path(remote_path)

        if connection:
            connection.get(remote_path, local_path)
        else:
            with self.create_connection() as connection:
                connection.get(remote_path, local_path)

        return local_path

    @connect
    def get_files(
        self,
        files_to_download=None,
        remote=None,
        connection=None,
        pattern=None,
        local_paths=None,
    ):
        """
        Download a list of files, either by providing the list explicitly, providing directories
        that contain files to download, or both.

        `Args:`
            files_to_download: list
                A list of full remote paths (can be relative) to files to download
            remote: str or list
                A path to a remote directory or a list of paths
            connection: obj
                An SFTP connection object
            pattern: str
                A regex pattern with which to select file names. Defaults to None, in which case
                all files will be selected.
            local_paths: list
                A list of paths to which to save the selected files. Defaults to None. If it is not
                the same length as the files to be fetched, temporary files are used instead.
        `Returns:`
            list
                Local paths where the files are saved.
        """

        if not (files_to_download or remote):
            raise ValueError(
                "You must provide either `files_to_download`, `remote`, or both, as "
                "an argument to `get_files`."
            )

        if not files_to_download:
            files_to_download = []

        if remote:
            try:  # assume `remote` is a str
                files_to_download.extend(self.list_files(remote, connection, pattern))
            except TypeError:  # if it's not a str it's a list
                files_to_download.extend(
                    f
                    for file_list in [
                        self.list_files(directory, connection, pattern) for directory in remote
                    ]
                    for f in file_list
                )

        if local_paths and len(local_paths) != len(files_to_download):
            logger.warning(
                "You provided a list of local paths for your files but it was not "
                "the same length as the files you are going to download.\nDefaulting to "
                "temporary files."
            )
            local_paths = []

        if local_paths:
            return [
                self.get_file(remote_path, local_path, connection)
                for local_path, remote_path in zip(local_paths, files_to_download)
            ]

        else:
            return [
                self.get_file(file, local_path=None, connection=connection)
                for file in files_to_download
            ]

    def get_table(self, remote_path, connection=None):
        """
        Download a csv from the server and convert into a Parsons table.

        The file may be compressed with gzip, or zip, but may not contain
        multiple files in the archive.

        `Args:`
            remote_path: str
                The remote path of the file to download
            connection: obj
                An SFTP connection object
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        if not file_utilities.valid_table_suffix(remote_path):
            raise ValueError("File type cannot be converted to a Parsons table.")

        return Table.from_csv(self.get_file(remote_path, connection=connection))

    def _convert_bytes_to_megabytes(self, size_in_bytes: int) -> int:
        result = int(size_in_bytes / (1024 * 1024))
        return result

    def _progress(self, transferred: int, to_be_transferred: int) -> None:
        """Return progress every 5 MB"""
        if self._convert_bytes_to_megabytes(transferred) % 5 != 0:
            return
        logger.info(
            f"Transferred: {self._convert_bytes_to_megabytes(transferred)} MB \t"
            f"out of: {self._convert_bytes_to_megabytes(to_be_transferred)} MB"
        )

    def put_file(
        self, local_path: str, remote_path: str, connection=None, verbose: bool = True
    ) -> None:
        """
        Put a file on the SFTP server

        `Args:`
            local_path: str
                The local path of the source file
            remote_path: str
                The remote path of the new file
            connection: obj
                An SFTP connection object
            verbose: bool
                Log progress every 5MB. Defaults to True.
        """
        if verbose:
            callback = self._progress
        else:
            callback = None
        if connection:
            connection.put(local_path, remote_path, callback=callback)
        else:
            with self.create_connection() as connection:
                connection.put(local_path, remote_path, callback=callback)

    def remove_file(self, remote_path, connection=None):
        """
        Delete a file on the SFTP server

        `Args:`
            remote_path: str
                The remote path of the file
            connection: obj
                An SFTP connection object
        """

        if connection:
            connection.remove(remote_path)
        else:
            with self.create_connection() as connection:
                connection.remove(remote_path)

    def get_file_size(self, remote_path, connection=None):
        """
        Get the size of a file in MB on the SFTP server. The file is
        not downloaded locally.

        `Args:`
            remote_path: str
                The remote path of the file
            connection: obj
                An SFTP connection object
        `Returns:`
            int
                The file size in MB.
        """

        if connection:
            size = connection.file(remote_path, "r")._get_size()
        else:
            with self.create_connection() as connection:
                size = connection.file(remote_path, "r")._get_size()

        return size / 1024

    @staticmethod
    def _list_contents(remote_path, connection, dir_pattern=None, file_pattern=None):

        dirs_to_return = []
        files_to_return = []
        dirs_and_files = [
            (S_ISDIR, dir_pattern, True, dirs_to_return),
            (S_ISREG, file_pattern, False, files_to_return),
        ]

        try:
            for entry in connection.listdir_attr(remote_path):
                entry_pathname = remote_path + "/" + entry.filename
                for method, pattern, do_search_full_path, paths in dirs_and_files:
                    string = entry_pathname if do_search_full_path else entry.filename
                    if method(entry.st_mode) and (not pattern or re.search(pattern, string)):
                        paths.append(entry_pathname)
        except FileNotFoundError:  # This error is raised when a directory is empty
            pass
        return dirs_to_return, files_to_return

    @connect
    def list_subdirectories(self, remote_path, connection=None, pattern=None):
        """
        List the subdirectories of a directory on the remote server.

        `Args:`
            remote_path: str
                The remote directory whose subdirectories will be listed
            connection: obj
                An SFTP connection object
            pattern: str
                A regex pattern with which to select full directory paths. Defaults to None, in
                which case all subdirectories will be selected.
        `Returns:`
            list
                The subdirectories in `remote_path`.
        """
        return self._list_contents(remote_path, connection, dir_pattern=pattern)[0]

    @connect
    def list_files(self, remote_path, connection=None, pattern=None):
        """
        List the files in a directory on the remote server.

        `Args:`
            remote_path: str
                The remote directory whose files will be listed
            connection: obj
                An SFTP connection object
            pattern: str
                A regex pattern with which to select file names. Defaults to None, in which case
                all files will be selected.
        `Returns:`
            list
                The files in `remote_path`.
        """
        return self._list_contents(remote_path, connection, file_pattern=pattern)[1]

    @connect
    def walk_tree(
        self,
        remote_path,
        connection=None,
        download=False,
        dir_pattern=None,
        file_pattern=None,
        max_depth=2,
    ):
        """
        Recursively walks a directory, fetching all subdirectories and files (as long as
        they match `dir_pattern` and `file_pattern`, respectively) and the maximum directory
        depth hasn't been exceeded. Optionally downloads discovered files.

        `Args:`
            remote_path: str
                The top level directory to walk
            connection: obj
                An SFTP connection object
            download: bool
                Whether to download discovered files
            dir_pattern: str
                A regex pattern with which to select directories. Defaults to None, in which case
                all directories will be selected.
            file_pattern: str
                A regex pattern with which to select files. Defaults to None, in which case
                all files will be selected.
            max_depth: int
                A limit on how many directories deep to traverse.  The default, 2, will search the
                contents of `remote_path` and its subdirectories.
        `Returns:`
            tuple
                A list of directories touched and a list of files.  If the files were downloaded
                the file list will consist of local paths, if not, remote paths.
        """

        if max_depth > 3:
            logger.warning(
                "Calling `walk_tree` with `max_depth` {}.  "
                "Recursively walking a remote directory will be much slower than a "
                "similar operation on a local file system.".format(max_depth)
            )

        to_return = self._walk_tree(
            remote_path,
            connection,
            download,
            dir_pattern,
            file_pattern,
            max_depth=max_depth,
        )

        return to_return

    def _walk_tree(
        self,
        remote_path,
        connection,
        download=False,
        dir_pattern=None,
        file_pattern=None,
        depth=0,
        max_depth=2,
    ):

        dir_list = []
        file_list = []

        depth += 1

        dirs, files = self._list_contents(remote_path, connection, dir_pattern, file_pattern)

        if download:
            self.get_files(files_to_download=files)

        if depth < max_depth:
            for directory in dirs:
                deeper_dirs, deeper_files = self._walk_tree(
                    directory,
                    connection,
                    download,
                    dir_pattern,
                    file_pattern,
                    depth,
                    max_depth,
                )
                dir_list.extend(deeper_dirs)
                file_list.extend(deeper_files)

        dir_list.extend(dirs)
        file_list.extend(files)

        return dir_list, file_list
