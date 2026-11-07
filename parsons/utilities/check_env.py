import os
from typing import Literal, TypeVar, overload

T = TypeVar("T")


@overload
def check(
    env: str,
    value: None = None,
    *,
    optional: Literal[True],
) -> str | None: ...


@overload
def check(
    env: str,
    value: None = None,
    *,
    optional: Literal[False] = False,
) -> str: ...


@overload
def check(
    env: str,
    value: T | None = ...,
    *,
    optional: Literal[False] = False,
) -> T | str: ...


@overload
def check(
    env: str,
    value: T | None = ...,
    *,
    optional: Literal[True],
) -> T | str | None: ...


def check(
    env: str,
    value: T | None = None,
    *,
    optional: bool = False,
) -> T | str | None:
    """
    Check if an environment variable has been set or value has been provided.

    Args:
        env:
            Name of environment variable to check.
        value:
            If provided, ignore environment variable and return this.

    Keyword Args:
        optional:
            If ``True``, return ``None`` if no value is found instead of raising ``KeyError``.

    Returns:
        The value of the requested environment variable (str) or the provided value (T).
        If called with ``optional=True``, will return ``None`` if no value is found or provided.

    Raises:
        KeyError: If no value is found/provided and `optional` is ``False``.

    .. version-changed:: v6.1.0

        Deprecated third positional argument `opt` in favor of `optional` keyword argument.

    .. version-changed:: v6.1.0

        Ranamed second positional argument `field` to `value`, adding deprecated `field` keyword argument for compatibility.

    .. version-changed:: v8.0.0

        Removed `opt` positional argument.

    .. version-changed:: v8.0.0

        Removed `field` keyword argument.

    """
    if value is not None:
        return value

    if (environment_variable := os.environ.get(env)) is not None:
        return environment_variable

    if optional:
        return None

    raise KeyError(f"No '{env}' found. Store as environment variable or pass as an argument.")
