from __future__ import annotations

import logging
from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import TYPE_CHECKING, Any, Protocol, TypeVar, runtime_checkable

from requests.auth import AuthBase
from requests.models import PreparedRequest
from typing_extensions import (
    Buffer,  # TODO: move to collections.abc when Python >= 3.12
)

if TYPE_CHECKING:
    from typing import TypeAlias

logger = logging.getLogger(__name__)


_T_co = TypeVar("_T_co", covariant=True)
_KT_co = TypeVar("_KT_co", covariant=True)
_VT_co = TypeVar("_VT_co", covariant=True)


@runtime_checkable
class SupportsItems(Protocol[_KT_co, _VT_co]):
    def items(self) -> Iterable[tuple[_KT_co, _VT_co]]: ...


@runtime_checkable
class SupportsRead(Protocol[_T_co]):
    def read(self, length: int = ..., /) -> _T_co: ...


_AuthType: TypeAlias = (
    tuple[str, str] | AuthBase | Callable[[PreparedRequest], PreparedRequest] | None
)
_HeadersType: TypeAlias = Mapping[str, str | bytes] | None
_JsonType: TypeAlias = (
    None | bool | int | float | str | Sequence["_JsonType"] | Mapping[str, "_JsonType"]
)
_ParamsMappingKeyType: TypeAlias = str | bytes | int | float
_ParamsMappingValueType: TypeAlias = (
    str | bytes | int | float | Iterable[str | bytes | int | float] | None
)
_ParamsType: TypeAlias = (
    SupportsItems[_ParamsMappingKeyType, _ParamsMappingValueType]
    | tuple[tuple[_ParamsMappingKeyType, _ParamsMappingValueType], ...]
    | Iterable[tuple[_ParamsMappingKeyType, _ParamsMappingValueType]]
    | str
    | bytes
    | None
)
_KVDataType: TypeAlias = Iterable[tuple[Any, Any]] | SupportsItems[Any, Any]
_DataType: TypeAlias = (
    _KVDataType | Iterable[bytes | str] | str | bytes | Buffer | SupportsRead[str | bytes] | None
)
