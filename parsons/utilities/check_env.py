import os
from typing import Optional


def check(env: str, field: Optional[str], optional: Optional[bool] = False) -> Optional[str]:
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
