import os
import warnings
from typing import TypeVar

T = TypeVar("T")


def check(
    env: str,
    value: T | None = None,
    opt: bool | None = None,
    *,
    optional: bool = False,
    field: T | None = None,
) -> T | str | None:
    """
    Check if an environment variable has been set or value has been provided.

    Args:
        env:
            Name of environment variable to check.
        value:
            If provided, ignore environment variable and return this.
        opt:
            Deprecated; use ``optional`` instead.
            If ``True``, return ``None`` if no value is found instead of raising ``KeyError``.

    Keyword Args:
        optional:
            If ``True``, return ``None`` if no value is found instead of raising ``KeyError``.
        field:
            Deprecated; use ``value`` instead.
            If provided, ignore environment variable and return this.

    Returns:
        The value of the requested environment variable (str) or the provided value (T).
        If called with ``optional=True``, will return ``None`` if no value is found or provided.

    Raises:
        KeyError: If no value is found/provided and ``optional`` is False.

    """
    # Handle deprecated arguments
    for name, val, replacement in (("opt", opt, "optional"), ("field", field, "value")):
        if val is None:
            continue

        warnings.warn(
            f"The '{name}' argument is deprecated; use '{replacement}' instead.",
            DeprecationWarning,
            stacklevel=2,
        )

    if (input_value := value if value is not None else field) is not None:
        return input_value

    if (environment_value := os.environ.get(env)) is not None:
        return environment_value

    if optional or opt:
        return None

    raise KeyError(f"No '{env}' found. Store as environment variable or pass as an argument.")
