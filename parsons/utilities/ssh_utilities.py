import asyncio
import logging
from typing import TYPE_CHECKING

import asyncssh
import psycopg2
from asyncssh import SSHClientConnection, SSHClientConnectionOptions, SSHForwarder, SSHListener

if TYPE_CHECKING:
    from psycopg2.extensions import connection as PostgresConnection


def query_through_ssh(
    ssh_host: str,
    ssh_port: int,
    ssh_username: str,
    ssh_password: str,
    db_host: str,
    db_port: int,
    db_name: str,
    db_username: str,
    db_password: str,
    query: str,
    *,
    ssh_config: list[str] | None = None,
    ssh_options: SSHClientConnectionOptions | None = None,
) -> list[tuple] | None:
    """
    Securely query a PostgreSQL database via an SSH tunnel.

    Args:
        ssh_host: str
            The host for the SSH connection
        ssh_port: int
            The port for the SSH connection
        ssh_username: str
            The username for the SSH connection
        ssh_password: str
            The password for the SSH connection
        db_host: str
            The host for the db connection
        db_port: int
            The port for the db connection
        db_name: str
            The name of the db database
        db_username: str
            The username for the db database
        db_password: str
            The password for the db database
        query: str
            The SQL query to execute
        ssh_config: SSHClientConnectionOptions, optional
            Paths to OpenSSH client configuration files to load
        ssh_options: SSHClientConnectionOptions, optional
            Options for establishing the SSH client connection, such as host key(s)

    Returns:
        list[tuple] | None
            A list of records resulting from the query or None if something went wrong

    """
    return asyncio.run(
        async_query_through_ssh(
            ssh_host=ssh_host,
            ssh_port=ssh_port,
            ssh_username=ssh_username,
            ssh_password=ssh_password,
            db_host=db_host,
            db_port=db_port,
            db_name=db_name,
            db_username=db_username,
            db_password=db_password,
            query=query,
            ssh_config=ssh_config,
            ssh_options=ssh_options,
        )
    )


async def async_query_through_ssh(
    ssh_host: str,
    ssh_port: int,
    ssh_username: str,
    ssh_password: str,
    db_host: str,
    db_port: int,
    db_name: str,
    db_username: str,
    db_password: str,
    query: str,
    *,
    ssh_config: list[str] | None = None,
    ssh_options: SSHClientConnectionOptions | None = None,
) -> list[tuple] | None:
    """
    Securely query a PostgreSQL database via an asynchronous SSH tunnel.

    Args:
        ssh_host: str
            The host for the SSH connection
        ssh_port: int
            The port for the SSH connection
        ssh_username: str
            The username for the SSH connection
        ssh_password: str
            The password for the SSH connection
        db_host: str
            The host for the db connection
        db_port: int
            The port for the db connection
        db_name: str
            The name of the db database
        db_username: str
            The username for the db database
        db_password: str
            The password for the db database
        query: str
            The SQL query to execute
        ssh_config: SSHClientConnectionOptions, optional
            Paths to OpenSSH client configuration files to load
        ssh_options: SSHClientConnectionOptions, optional
            Options for establishing the SSH client connection, such as host key(s)

    Returns:
        list[tuple] | None
            A list of records resulting from the query or None if something went wrong

    """
    ssh_conn: SSHClientConnection | None = None
    tunnel: SSHListener | SSHForwarder | None = None

    def _execute_sync_query(assigned_port: int) -> list[tuple]:
        db_conn: PostgresConnection | None = None

        try:
            db_conn = psycopg2.connect(
                host="127.0.0.1",
                port=assigned_port,
                user=db_username,
                password=db_password,
                database=db_name,
            )
            with db_conn.cursor() as cur:
                cur.execute(query)
                return cur.fetchall()

        except psycopg2.Error as db_err:
            logging.error(f"PostgreSQL Error: {db_err}")
            raise

        finally:
            if db_conn:
                db_conn.close()

    try:
        ssh_conn = await asyncssh.connect(
            ssh_host,
            port=ssh_port,
            username=ssh_username,
            password=ssh_password,
            config=ssh_config,
            options=ssh_options,
            known_hosts=None if ssh_options is None else getattr(ssh_options, "known_hosts", None),
        )
        logging.info("SSH connection established.")

        tunnel = await ssh_conn.forward_local_port("", 0, db_host, db_port)
        local_port = tunnel.get_port()
        logging.info(f"Tunnel active on localhost:{local_port}")

        output = await asyncio.to_thread(_execute_sync_query, local_port)
        logging.info(f"Query successful: {len(output) if output else 0} rows returned.")

    except (psycopg2.Error, asyncssh.Error, OSError):
        raise

    finally:
        if tunnel:
            tunnel.close()
            await tunnel.wait_closed()
            logging.info("SSH tunnel closed.")

        if ssh_conn:
            ssh_conn.close()
            await ssh_conn.wait_closed()
            logging.info("SSH connection closed.")

    return output or None
