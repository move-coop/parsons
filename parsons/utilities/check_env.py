import os


def check(env, field=None):
    """Check if an envrionment variable is set for __init__"""
    if not field:
        try:
            return os.environ[env]
        except KeyError:
            raise KeyError(f'No {env} found. Store as environment variable or '
                           f'pass as an argument.')
    return field
