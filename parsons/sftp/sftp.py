from contextlib import contextmanager
import paramiko
import os
import re
from stat import S_ISDIR, S_ISREG
from argparse import ArgumentError
from itertools import chain

from parsons.utilities import files
from parsons.etl import Table


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
            raise ValueError("Missing password or ssh authentication key")

        self.password = password
        self.rsa_private_key_file = rsa_private_key_file
        self.port = port

    @contextmanager
    def create_connection(self):
        """
        Create an SFTP connection. You can then utilize this in a ``with`` block
        and it will close the connection when it is out of scope. You should use
        this when you wish to batch multiple methods using a single connection.

        .. code-block:: python

            import SFTP

            sftp = SFTP()
            connection = sftp.create_connection()

            with connection as conn:
                sftp.make_directory('my_dir', connection=conn)
                sftp.put_file('my_csv.csv', connection=conn)

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

    def list_directory(self, remote_path='.', connection=None):
        """
        List the contents of a directory

        `Args:`
            remote_path: str
                The remote path of the directory
            connection: obj
                An SFTP connection object
        `Returns:`
            list
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
            local_path = files.create_temp_file_for_path(remote_path)

        if connection:
            connection.get(remote_path, local_path)
        with self.create_connection() as connection:
            connection.get(remote_path, local_path)

        return local_path

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

        if not files.valid_table_suffix(remote_path):
            raise ValueError('File type cannot be converted to a Parsons table.')

        return Table.from_csv(self.get_file(remote_path, connection=connection))

    def put_file(self, local_path, remote_path, connection=None):
        """
        Put a file on the SFTP server
        `Args:`
            local_path: str
                The local path of the source file
            remote_path: str
                The remote path of the new file
            connection: obj
                An SFTP connection object
        """
        if connection:
            connection.put(local_path, remote_path)
        with self.create_connection() as connection:
            connection.put(local_path, remote_path)

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
            size = connection.file(remote_path, 'r')._get_size()
        else:
            with self.create_connection() as connection:
                size = connection.file(remote_path, 'r')._get_size()

        return size / 1024

    @staticmethod
    def _list_contents(remote_path, method, connection, pattern=None):
        return [
            remote_path + "/" + entry.filename
            for entry in connection.listdir_attr(remote_path)
            if method(entry.mode)
            and (not pattern or re.match(pattern, remote_path))
        ]

    def list_subdirectories(self, remote_path, connection=None, pattern=None):
        if not connection:
            connection = self.create_connection()
        with connection:
            return self._list_contents(remote_path, S_ISDIR, connection=connection, pattern=pattern)

    def list_files(self, remote_path, connection=None, pattern=None):
        if not connection:
            connection = self.create_connection()
        with connection:
            return self._list_contents(remote_path, S_ISREG, connection=connection, pattern=pattern)

    def get_files(self, files_to_download=None, remote_path=None, connection=None, pattern=None, local_paths=None):

        if not files_to_download or remote_path:
            raise ValueError("You must provide either `files_to_download`, `remote_path`, or both, as an "
                             "argument to `get_files`.")

        if not connection:
            connection = self.create_connection()

        if not files_to_download:
            files_to_download =[]

        if remote_path:
            files_to_download.extend(self.list_files(self, remote_path, connection, pattern))

        if local_paths and len(local_paths) != len(files_to_download):
            print("You provided a list of local paths for your files but it was not the same length as the files you"
                  "are going to download. Defaulting to temporary files.")
            local_paths = []

        if local_paths:
            local_paths_remote_paths = zip(local_paths, files_to_download)
            return [
                self.get_file(remote_path, local_path, connection)
                for local_path, remote_path in local_paths_remote_paths
            ]

        else:
            return [
                self.get_file(file, local_path=None, connection=connection)
                for file in files_to_download
            ]

    def match_dirs_and_files(self, remote_path, dir_pattern, connection=None, file_pattern=None, download=False):

        if not connection:
            connection = self.create_connection()

        retrieval_method = self.get_files if download else self.list_files
        subdirectories = self.list_subdirectories(remote_path, connection, dir_pattern)
        return chain.from_iterable([retrieval_method(d, connection, file_pattern) for d in subdirectories])

    def walk_tree(self, connection, remote_path, download=False, dir_pattern=None, file_pattern=None, dir_list=None,
                   file_list=None):

        for lst in dir_list, file_list:
            if not lst:
                lst = []

        retrieval_method = self.get_files if download else self.list_files

        new_file_list = retrieval_method(remote_path, connection, file_pattern)
        new_dir_list = self.list_subdirectories(remote_path, connection, dir_pattern)

        for old, new in [(dir_list, new_dir_list), (file_list, new_file_list)]:
            old.extend(new)

        for directory in new_dir_list:
            self._walk_tree(connection, directory, retrieval_method, dir_pattern, file_pattern, file_list)

        return dir_list, file_list



