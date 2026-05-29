import os
import warnings
from typing import Literal, TypeVar, overload

T = TypeVar("T")


@overload
def check(
    env: str,
    value: T,
    opt: bool | None = ...,
    *,
    optional: bool = ...,
    field: T | None = ...,
) -> T: ...


@overload
def check(
    env: str,
    value: None = None,
    opt: bool | None = ...,
    *,
    optional: Literal[True],
    field: None = None,
) -> str | None: ...


@overload
def check(
    env: str,
    value: None = None,
    opt: bool | None = ...,
    *,
    optional: Literal[False] = False,
    field: None = None,
) -> str: ...


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
            Deprecated; use `optional` instead.
            If ``True``, return ``None`` if no value is found instead of raising ``KeyError``.

    Keyword Args:
        optional:
            If ``True``, return ``None`` if no value is found instead of raising ``KeyError``.
        field:
            Deprecated; use `value` instead.
            If provided, ignore environment variable and return this.

    Returns:
        The value of the requested environment variable (str) or the provided value (T).
        If called with ``optional=True``, will return ``None`` if no value is found or provided.

    Raises:
        KeyError: If no value is found/provided and `optional` is ``False``.

    """
    # Handle deprecated arguments
    if opt is not None:
        warnings.warn(
            "The 'opt' positional argument is deprecated. "
            "Use the 'optional' keyword argument. "
            "Overriding 'optional' with value of 'opt' for backwards-compatibility.",
            DeprecationWarning,
            stacklevel=2,
        )
        optional = opt

    if field is not None:
        warnings.warn(
            "The 'field' keyword argument is deprecated. "
            "Use the 'value' positional or keyword argument. "
            "Overriding 'value' with value of 'field' for backwards-compatibility.",
            DeprecationWarning,
            stacklevel=2,
        )
        value = field

    if value is not None:
        return value

    if (environment_variable := os.environ.get(env)) is not None:
        return environment_variable

    if optional:
        return None

    raise KeyError(f"No '{env}' found. Store as environment variable or pass as an argument.")
