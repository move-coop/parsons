from types import SimpleNamespace

import pytest


@pytest.fixture
def ssh_mocks(mocker):
    """Patch the two external libraries ``query_through_ssh`` talks to.

    The function opens an ``sshtunnel.SSHTunnelForwarder`` and a ``psycopg2``
    connection — both third-party boundaries — so we replace them and let the real
    function run its tunnel/connect/query/cleanup flow against the fakes. Returns the
    patched callables and their instances (``server``, ``con``, ``cursor``).
    """
    tunnel = mocker.patch("parsons.utilities.ssh_utilities.sshtunnel.SSHTunnelForwarder")
    connect = mocker.patch("parsons.utilities.ssh_utilities.psycopg2.connect")
    server = tunnel.return_value
    server.local_bind_port = 12345
    con = connect.return_value
    cursor = con.cursor.return_value
    return SimpleNamespace(tunnel=tunnel, connect=connect, server=server, con=con, cursor=cursor)
