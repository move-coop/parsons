import os
from typing import Any


def check(env: str, value: Any | None = None, *, optional: bool = False) -> Any | None:
    """
    Check if an environment variable has been set or value has been provided.

    Args:
        env: str
            Name of environment variable to check.
        value: Any, optional
            If provided, ignore environment variable and use this.

    Keyword Args:
        optional: bool, optional
            If true, do not raise an error if no value is found or provided.

    Returns:
        Any
            The value of the requested environment variable (str) or the provided value (Any).
            May return None if no value is found or provided, if called with optional=True.

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
