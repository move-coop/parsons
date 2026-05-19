import os


def check(env: str, field: str | None, optional: bool | None = False) -> str | None:
    """
    Check if an environment variable has been set. If it has not been set
    and the passed field or arguments have not been passed, then raise an
    error.
    """
    if field:
        return field
    try:
        return os.environ[env]
    except KeyError as e:
        if not optional:
            raise KeyError(
                f"No {env} found. Store as environment variable or pass as an argument."
            ) from e
