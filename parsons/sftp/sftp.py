from contextlib import contextmanager
import paramiko
from parsons.utilities import files


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
    def _create_connection(self):
        # Internal method to create a connection and close when it's out of scope.
        # Make sure to use this in a ``with`` block, since it's a context manager.
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

    def list_directory(self, remote_path='.'):
        """
        List the contents of a directory

        `Args:`
            remote_path: str
                The remote path of the directory
        `Returns:`
            list
        """

        with self._create_connection() as conn:
            file_list = conn.listdir(path=remote_path)

        return file_list

    def make_directory(self, remote_path):
        """
        Makes a new directory on the SFTP server

        `Args:`
            remote_path: str
                The remote path of the directory
        """

        with self._create_connection() as conn:
            conn.mkdir(remote_path)

    def remove_directory(self, remote_path):
        """
        Remove a directory from the SFTP server

        `Args:`
            remote_path: str
                The remote path of the directory
        """

        with self._create_connection() as conn:
            conn.rmdir(remote_path)

    def get_file(self, remote_path, local_path=None):
        """
        Download a file from the SFTP server

        `Args:`
            remote_path: str
                The remote path of the file to download
            local_path: str
                The local path where the file will be downloaded. If not specified, a temporary
                file will be created and returned, and that file will be removed automatically
                when the script is done running.

        `Returns:`
            str
                The path of the local file
        """

        if not local_path:
            local_path = files.create_temp_file_for_path(remote_path)

        with self._create_connection() as conn:
            conn.get(remote_path, local_path)

        return local_path

    def put_file(self, local_path, remote_path):
        """
        Put a file on the SFTP server
        `Args:`
            local_path: str
                The local path of the source file
            remote_path: str
                The remote path of the new file
        """
        with self._create_connection() as conn:
            conn.put(local_path, remote_path)

    def remove_file(self, remote_path):
        """
        Delete a file on the SFTP server

        `Args:`
            remote_path: str
                The remote path of the file
        """

        with self._create_connection() as conn:
            conn.remove(remote_path)

    def get_file_size(self, remote_path):
        """
        Get the size of a file in MB on the SFTP Server

        `Args:`
            remote_path: str
                The remote path of the file
        `Returns:`
            int
                The file size in MB.
        """

        with self._create_connection() as conn:
            size = conn.file(remote_path, 'r')._get_size()

        return size / 1024
