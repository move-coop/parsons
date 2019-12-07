import os


def check(env, field, *args):
    """
    Check if an environment variable has been set. If it has not been set
    and the passed field or arguments have not been passed, then raise an
    error.
    """
    if not field and not args:
        try:
            return os.environ[env]
        except KeyError:
            raise KeyError(f'No {env} found. Store as environment variable or '
                           f'pass as an argument.')
    return field
