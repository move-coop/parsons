import os


def check(env: str, value: str | bool | int | None = None, *, optional: bool = False) -> str | None:
    """
    Check if an environment variable has been set or value has been provided.

    Args:
        env: str
            Name of environment variable to check.
        value: str | bool | int, optional
            If provided, ignore environment variable and use this.

    Keyword Args:
        optional: bool, optional
            If true, do not raise an error if no value is found or provided.

    Raises:
        KeyError
            If there is no matching environment variable or provided value.

    """
    if value is not None:
        return value

    try:
        return os.environ[env]

    except KeyError as e:
        if optional:
            return None

        raise KeyError(
            f"No {env} found. Store as environment variable or pass as an argument."
        ) from e
