from sshtunnel import SSHTunnelForwarder


class SSHTunnelUtility:
    """
    A utility class for managing SSH tunnels.

    `Args`:
        ssh_host (str): The hostname or IP address of the SSH server.
        ssh_port (int): The port number of the SSH server. Defaults to 22.
        ssh_username (str): The username to authenticate with.
        ssh_password (str): The password to authenticate with.
        remote_bind_address (tuple): A tuple of the address (host) and port of the remote service.

    `Returns`:
        SSHTunnelUtility: An instance of the SSHTunnelUtility class.
    """

    def __init__(
        self,
        ssh_host=None,
        ssh_port=22,
        ssh_username=None,
        ssh_password=None,
        remote_bind_address=None,
    ):
        self.ssh_host = ssh_host
        self.ssh_port = ssh_port
        self.ssh_username = ssh_username
        self.ssh_password = ssh_password
        self.remote_bind_address = remote_bind_address
        self.server = None

    def __enter__(self):
        """
        Start the SSH tunnel on entering the context.

        This method sets up the SSH tunnel using the provided credentials and
        connection details, and starts the tunnel.

        `Returns`:
            SSHTunnelForwarder: The active tunnel server instance, which can be
            used to interact with the remote service through a local port.
        """
        self.server = SSHTunnelForwarder(
            (self.ssh_host, self.ssh_port),
            ssh_username=self.ssh_username,
            ssh_password=self.ssh_password,
            remote_bind_address=self.remote_bind_address,
        )
        self.server.start()
        return self.server

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Stop the SSH tunnel on exiting the context.

        This method is called when exiting the context of the `with` statement.
        It stops the SSH tunnel and cleans up the resources, ensuring that the
        connection is closed properly, even if an exception occurs within the
        context block.

        `Args`:
            exc_type: Exception type if an exception was raised in the context.
            exc_val: Exception value if an exception was raised.
            exc_tb: Traceback object if an exception was raised.

        `Returns`:
            None
        """
        if self.server:
            self.server.stop()
