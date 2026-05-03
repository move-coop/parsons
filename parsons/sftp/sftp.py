import logging
import re
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from stat import S_ISDIR, S_ISREG

import paramiko

from parsons import Table
from parsons.sftp.utilities import connect
from parsons.utilities import files as file_utilities

logger = logging.getLogger(__name__)


class SFTP:
    """
    Instantiate SFTP Class

    Args:
        host: The host name
        username: The user name
        password: The password
        port: Specify if different than the standard port 22.
        rsa_private_key_file:
            Absolute path to a private RSA key used to authenticate stfp connection.
        paramiko_pkey: A paramiko RSAKey object to be passed directly.
        timeout: Timeout argument for use when getting files through SFTP.

    """

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int = 22,
        rsa_private_key_file: str | None = None,
        paramiko_pkey: paramiko.RSAKey | None = None,
        timeout: int | None = None,
    ) -> None:
        self.host = host
        if not self.host:
            raise ValueError("Missing the SFTP host name")

        self.username = username
        if not self.username:
            raise ValueError("Missing the SFTP username")

        if not (password or rsa_private_key_file or paramiko_pkey):
            raise ValueError("Missing password or SSH authentication key")

        self.password = password
        self.paramiko_pkey = paramiko_pkey
        self.rsa_private_key_file = rsa_private_key_file
        self.port = port
        self.timeout = timeout

    @contextmanager
    def create_connection(self) -> Generator[paramiko.SFTPClient, None, None]:
        """
        Create an SFTP connection.

        Yields:
            SFTP Connection object

        """
        transport = paramiko.Transport((self.host, self.port))
        pkey = self.paramiko_pkey
        if self.rsa_private_key_file:
            # we need to read it in
            pkey = paramiko.RSAKey.from_private_key_file(self.rsa_private_key_file)

        transport.connect(
            username=self.username,
            password=self.password,
            pkey=pkey,
        )
        conn: paramiko.SFTPClient = paramiko.SFTPClient.from_transport(transport)
        if self.timeout:
            conn.get_channel().settimeout(self.timeout)
        yield conn
        conn.close()
        transport.close()

    def list_directory(
        self, remote_path: str = ".", connection: paramiko.SFTPClient | None = None
    ) -> list[str]:
        """
        List the contents of a directory

        Args:
            remote_path: The remote path of the directory.
            connection: An SFTP connection object.

        Returns:
            A list of files and subdirectories in the provided directory.

        """
        if connection:
            return connection.listdir(path=remote_path)

        with self.create_connection() as connection:
            return connection.listdir(path=remote_path)

    def make_directory(
        self, remote_path: str, connection: paramiko.SFTPClient | None = None
    ) -> None:
        """
        Makes a new directory on the SFTP server

        Args:
            remote_path: The remote path of the directory.
            connection: An SFTP connection object.

        """
        if connection:
            connection.mkdir(remote_path)
        else:
            with self.create_connection() as connection:
                connection.mkdir(remote_path)

    def remove_directory(
        self, remote_path: str, connection: paramiko.SFTPClient | None = None
    ) -> None:
        """
        Remove a directory from the SFTP server

        Args:
            remote_path: The remote path of the directory.
            connection: An SFTP connection object.

        """
        if connection:
            connection.rmdir(remote_path)
        else:
            with self.create_connection() as connection:
                connection.rmdir(remote_path)

    def get_file(
        self,
        remote_path: str,
        local_path: Path | str | None = None,
        connection=None,
        export_chunk_size: int | None = None,
    ) -> str:
        """
        Download a file from the SFTP server

        Args:
            remote_path:
                The remote path of the file to download
            local_path:
                The local path where the file will be downloaded.
                If not specified, a temporary file will be created and returned,
                and that file will be removed automatically when the script is done running.
            connection:
                An SFTP connection object
            export_chunk_size:
                Size in bytes to iteratively export from the remote server.

        Returns:
            The path of the local file

        """
        if not local_path:
            local_path = Path(file_utilities.create_temp_file_for_path(remote_path))

        if connection:
            if export_chunk_size:
                self.__get_file_in_chunks(
                    remote_path=remote_path,
                    local_path=local_path,
                    connection=connection,
                    export_chunk_size=export_chunk_size,
                )
            else:
                connection.get(remote_path, str(local_path))

        else:
            with self.create_connection() as connection:
                if export_chunk_size:
                    self.__get_file_in_chunks(
                        remote_path=remote_path,
                        local_path=local_path,
                        connection=connection,
                        export_chunk_size=export_chunk_size,
                    )
                else:
                    connection.get(remote_path, str(local_path))

        return str(local_path)

    def __get_file_in_chunks(
        self, remote_path: str, local_path: Path | str, connection, export_chunk_size: int
    ) -> None:
        """
        Download a file in chunked-increments from the remote host to the local path

        Args:
            remote_path: The remote path of the file to download.
            local_path:
                The local path where the file will be downloaded.
                If not specified, a temporary file will be created and returned,
                and that file will be removed automatically when the script is done running.
            connection: An SFTP connection object.
            export_chunk_size: Size in bytes to iteratively export from the remote server.

        """
        logger.info(f"Reading from {remote_path} to {local_path} in {export_chunk_size}B chunks")

        with connection.open(remote_path, "rb") as _remote_file:
            # This disables paramiko's prefetching behavior
            _remote_file.set_pipelined(False)

            while True:
                # Read in desired number of rows from the server
                response = _remote_file.read(export_chunk_size)

                # Break the loop if there are no records to read
                if not response:
                    break

                # Write to the destination file
                Path(local_path).write_bytes(response)
                logger.debug("Successfully read %s rows to %s", export_chunk_size, local_path)

    @connect
    def get_files(
        self,
        files_to_download: list[str] | None = None,
        remote: str | list[str] | None = None,
        connection: paramiko.SFTPClient | None = None,
        pattern: str | None = None,
        local_paths: list[Path | str] | None = None,
    ) -> list[str]:
        """
        Download a list of files.

        Can provide the list explicitly,
        or provide directories that contain files to download, or both.

        Args:
            files_to_download: A list of full remote paths (can be relative) to files to download.
            remote: A path to a remote directory or a list of paths.
            connection: An SFTP connection object
            pattern:
                A regex pattern with which to select file names.
                Defaults to None, in which case all files will be selected.
            local_paths:
                A list of paths to which to save the selected files.
                Defaults to None.
                If it is not the same length as the files to be fetched,
                temporary files are used instead.

        Returns:
            Local paths where the files are saved.

        """
        if not (files_to_download or remote):
            raise ValueError(
                "You must provide either `files_to_download`, `remote`, or both, "
                "as an argument to `get_files`."
            )

        if not files_to_download:
            files_to_download = []

        if remote:
            remotes = [remote] if isinstance(remote, str) else remote
            for directory in remotes:
                files = self.list_files(directory, connection, pattern)
                files_to_download.extend(files)

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
                for local_path, remote_path in zip(local_paths, files_to_download, strict=False)
            ]

        return [
            self.get_file(file, local_path=None, connection=connection)
            for file in files_to_download
        ]

    def get_table(self, remote_path: str, connection: paramiko.SFTPClient | None = None) -> Table:
        """
        Download a csv from the server and convert into a Parsons table.

        The file may be compressed with gzip, or zip,
        but may not contain multiple files in the archive.

        Args:
            remote_path: The remote path of the file to download.
            connection: An SFTP connection object.

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
        self, local_path: Path | str, remote_path: str, connection=None, verbose: bool = True
    ) -> None:
        """
        Put a file on the SFTP server

        Args:
            local_path: The local path of the source file.
            remote_path: The remote path of the new file.
            connection: An SFTP connection object
            verbose:
                Log progress every 5MB.
                Defaults to True.

        """
        callback = self._progress if verbose else None
        if connection:
            connection.put(str(local_path), remote_path, callback=callback)
        else:
            with self.create_connection() as connection:
                connection.put(str(local_path), remote_path, callback=callback)

    def remove_file(self, remote_path: str, connection: paramiko.SFTPClient | None = None) -> None:
        """
        Delete a file on the SFTP server.

        Args:
            remote_path: The remote path of the file.
            connection: An SFTP connection object.

        """
        if connection:
            connection.remove(remote_path)
        else:
            with self.create_connection() as connection:
                connection.remove(remote_path)

    def get_file_size(self, remote_path: str, connection: paramiko.SFTPClient | None = None) -> int:
        """
        Get the size of a file in MB on the SFTP server.

        The file is not downloaded locally.

        Args:
            remote_path: The remote path of the file.
            connection: An SFTP connection object.

        Returns:
            The file size in MB.

        """
        if connection:
            size = connection.file(remote_path, "r")._get_size()
        else:
            with self.create_connection() as connection:
                size = connection.file(remote_path, "r")._get_size()

        return size / 1024

    @staticmethod
    def _list_contents(
        remote_path: str,
        connection: paramiko.SFTPClient,
        dir_pattern: str | None = None,
        file_pattern: str | None = None,
    ) -> tuple[list[str], list[str]]:
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
    def list_subdirectories(
        self,
        remote_path: str,
        connection: paramiko.SFTPClient,
        pattern: str | None = None,
    ) -> list[str]:
        """
        List the subdirectories of a directory on the remote server.

        Args:
            remote_path: The remote directory whose subdirectories will be listed
            connection: An SFTP connection object
            pattern:
                A regex pattern with which to select full directory paths.
                Defaults to ``None``, in which case all subdirectories will be selected.

        Returns:
            The subdirectories in `remote_path`.

        """
        return self._list_contents(remote_path, connection, dir_pattern=pattern)[0]

    @connect
    def list_files(
        self,
        remote_path: str,
        connection: paramiko.SFTPClient,
        pattern: str | None = None,
    ) -> list[str]:
        """
        List the files in a directory on the remote server.

        Args:
            remote_path: The remote directory whose files will be listed
            connection: An SFTP connection object
            pattern:
                A regex pattern with which to select file names.
                Defaults to ``None``, in which case all files will be selected.

        Returns:
            The files in `remote_path`.

        """
        return self._list_contents(remote_path, connection, file_pattern=pattern)[1]

    @connect
    def walk_tree(
        self,
        remote_path: str,
        connection: paramiko.SFTPClient,
        download: bool = False,
        dir_pattern: str | None = None,
        file_pattern: str | None = None,
        max_depth: int = 2,
    ) -> tuple[list[str], list[str]]:
        """
        Recursively walks a directory, fetching all subdirectories and files (as long as
        they match `dir_pattern` and `file_pattern`, respectively) and the maximum directory
        depth hasn't been exceeded. Optionally downloads discovered files.

        Args:
            remote_path: The top level directory to walk
            connection: An SFTP connection object
            download:
                Whether to download discovered files
            dir_pattern:
                A regex pattern with which to select directories.
                Defaults to ``None``, in which case all directories will be selected.
            file_pattern:
                A regex pattern with which to select files.
                Defaults to ``None``, in which case all files will be selected.
            max_depth:
                A limit on how many directories deep to traverse.
                The default, ``2``, will search the contents of `remote_path` and its subdirectories.

        Returns:
            A list of directories touched and a list of files.
            If the files were downloaded the file list will consist
            of local paths, if not, remote paths.

        """
        if max_depth > 3:
            logger.warning(
                f"Calling `walk_tree` with `max_depth` {max_depth}.  "
                "Recursively walking a remote directory will be much slower than a "
                "similar operation on a local file system."
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
        remote_path: str,
        connection: paramiko.SFTPClient,
        download: bool = False,
        dir_pattern: str | None = None,
        file_pattern: str | None = None,
        depth: int = 0,
        max_depth: int = 2,
    ) -> tuple[list[str], list[str]]:
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
