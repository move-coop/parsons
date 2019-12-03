import os


def check(env, field=None, *args):
    """Check if an environment variable is set for __init__"""
    if not field and not args:
        try:
            return os.environ[env]
        except KeyError:
            raise KeyError(f'No {env} found. Store as environment variable or '
                           f'pass as an argument.')
    return field
