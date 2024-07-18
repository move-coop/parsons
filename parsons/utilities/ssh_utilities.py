import logging
import sshtunnel
import psycopg2


def query_through_ssh(
    ssh_host,
    ssh_port,
    ssh_username,
    ssh_password,
    db_host,
    db_port,
    db_name,
    db_username,
    db_password,
    query,
):
    """
    `Args:`
        ssh_host:
            The host for the SSH connection
        ssh_port:
            The port for the SSH connection
        ssh_username:
            The username for the SSH connection
        ssh_password:
            The password for the SSH connection
        db_host:
            The host for the db connection
        db_port:
            The port for the db connection
        db_name:
            The name of the db database
        db_username:
            The username for the db database
        db_password:
            The password for the db database
        query:
            The SQL query to execute

    `Returns:`
        A list of records resulting from the query or None if something went wrong
    """
    output = None
    server = None
    con = None
    try:
        server = sshtunnel.SSHTunnelForwarder(
            (ssh_host, int(ssh_port)),
            ssh_username=ssh_username,
            ssh_password=ssh_password,
            remote_bind_address=(db_host, int(db_port)),
        )
        server.start()
        logging.info("SSH tunnel established successfully.")

        con = psycopg2.connect(
            host="localhost",
            port=server.local_bind_port,
            database=db_name,
            user=db_username,
            password=db_password,
        )
        logging.info("Database connection established successfully.")

        cursor = con.cursor()
        cursor.execute(query)
        records = cursor.fetchall()
        output = records
        logging.info(f"Query executed successfully: {records}")
    except Exception as e:
        logging.error(f"Error during query execution: {e}")
        raise e
    finally:
        if con:
            con.close()
            logging.info("Database connection closed.")
        if server:
            server.stop()
            logging.info("SSH tunnel closed.")
    return output
