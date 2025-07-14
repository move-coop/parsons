from typing import Any, Iterable, Mapping, Optional, Text, Union

import requests

Data = Optional[
    Union[
        Iterable[bytes],
        str,
        bytes,
        list[tuple[Any, Any]],
        tuple[tuple[Any, Any], ...],
        Mapping[Any, Any],
    ]
]

Response = requests.models.Response


class APIConnector:
    def __init__(self, *, session, uri, **kwargs):
        self.session = session
        self.uri = uri

    def get_request(self, endpoint: Union[str, bytes, Text], **kwargs) -> Response:
        r"""Sends a GET request. Returns :class:`Response` object."""
        url = self.uri + endpoint
        return self.session.get(url, **kwargs)

    def options_request(self, endpoint: Union[str, bytes, Text], **kwargs) -> Response:
        r"""Sends a OPTIONS request. Returns :class:`Response` object."""
        url = self.uri + endpoint
        return self.session.options(url, **kwargs)

    def head_request(self, endpoint: Union[str, bytes, Text], **kwargs) -> Response:
        r"""Sends a HEAD request. Returns :class:`Response` object."""
        url = self.uri + endpoint
        return self.session.head(url, **kwargs)

    def post_request(
        self,
        endpoint: Union[str, bytes, Text],
        data: Data = None,
        json: Optional[Any] = None,
        **kwargs,
    ) -> Response:
        r"""Sends a POST request. Returns :class:`Response` object."""
        url = self.uri + endpoint
        return self.session.post(url, data=data, json=json, **kwargs)

    def put_request(
        self, endpoint: Union[str, bytes, Text], data: Data = None, **kwargs
    ) -> Response:
        r"""Sends a PUT request. Returns :class:`Response` object."""

        url = self.uri + endpoint
        return self.session.put(url, data=data, **kwargs)

    def patch_request(self, endpoint: Union[str, bytes, Text], data=None, **kwargs):
        r"""Sends a PATCH request. Returns :class:`Response` object."""
        url = self.uri + endpoint
        return self.session.patch(url, data=data, **kwargs)

    def delete_request(self, endpoint: Union[str, bytes, Text], **kwargs) -> Response:
        r"""Sends a DELETE request. Returns :class:`Response` object."""

        url = self.uri + endpoint
        return self.session.delete("DELETE", url, **kwargs)
