from functools import wraps
import paramiko


def connection_exists(args, kwargs):
    if any([isinstance(arg, paramiko.sftp_client.SFTPClient) for arg in args]):
        return True
    if "connection" in kwargs and kwargs["connection"]:
        return True
    return False


def connect(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not connection_exists(args, kwargs):
            with args[0].create_connection() as connection:
                kwargs["connection"] = connection
                return func(*args, **kwargs)
        else:
            return func(*args, **kwargs)

    return wrapper
