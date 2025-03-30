import os
from typing import NoReturn, Optional, Union


def check(env: str, field: Optional[str], optional: Optional[bool] = False) -> Union[str, NoReturn]:
    """
    Check if an environment variable has been set. If it has not been set
    and the passed field or arguments have not been passed, then raise an
    error.
    """
    if not field:
        try:
            return os.environ[env]
        except KeyError:
            if not optional:
                raise KeyError(
                    f"No {env} found. Store as environment variable or pass as an argument."
                )
    return field
