from datetime import datetime, timezone

import pytest
from requests_mock import Mocker

from parsons import PDI


# Need to provide environment variables
# PDI_USERNAME, PDI_PASSWORD, PDI_API_TOKEN
@pytest.mark.live
def test_connection() -> None:
    PDI(qa_url=True)


@pytest.mark.parametrize(
    ("username", "password", "api_token"),
    [
        (None, None, None),
        (None, "pass", "token"),
        ("user", None, "token"),
        ("user", "pass", None),
    ],
)
def test_init_error(
    username: str | None,
    password: str | None,
    api_token: str | None,
    monkeypatch: pytest.MonkeyPatch,
):
    for env_var in ("PDI_USERNAME", "PDI_PASSWORD", "PDI_API_TOKEN"):
        monkeypatch.delenv(env_var, raising=False)

    with pytest.raises(KeyError, match="Store as environment variable or pass as an argument"):
        PDI(username, password, api_token)


@pytest.mark.parametrize(
    ("obj", "exp_obj"),
    [
        ({"a": "a", "b": None, "c": "c"}, {"a": "a", "c": "c"}),
        (
            [{"a": "a", "b": None, "c": "c"}, {"a": "a", "c": None}],
            [{"a": "a", "c": "c"}, {"a": "a"}],
        ),
        ("string", "string"),
    ],
)
def test_clean_dict(
    mock_pdi: PDI,
    obj: dict[str, str | None] | list[dict[str, str | None]] | str,
    exp_obj: dict[str, str] | list[dict[str, str]] | str,
):
    assert mock_pdi._clean_dict(obj) == exp_obj


@pytest.mark.parametrize("request_method", ["GET", "POST", "PUT", "DELETE"])
def test_authentication_header(mock_pdi: PDI, requests_mock: Mocker, request_method: str) -> None:
    """Ensure that the authentication header is included in requests."""
    requests_mock.reset_mock()

    request_url = "https://apiqa.bluevote.com"
    requests_mock.request(request_method, request_url)
    mock_pdi._request(request_url, req_type=request_method)

    history = requests_mock.request_history
    for request in history:
        assert "Authorization" in request.headers
        assert request.headers["Authorization"] == "Bearer AccessToken"


@pytest.mark.parametrize("request_method", ["GET", "POST", "PUT", "DELETE"])
def test_authentication_header_refresh(
    mock_pdi: PDI, requests_mock: Mocker, request_method: str
) -> None:
    """Ensure that the authentication header is included in requests and is refreshed if expired."""
    # Queue authentication response with expired token, and load it into PDI
    requests_mock.post(
        "https://apiqa.bluevote.com/sessions",
        json={
            "AccessToken": "AccessTokenExpired",
            "ExpirationDate": "2026-01-01",
        },
    )
    mock_pdi._get_session_token()
    requests_mock.reset_mock()
    current_datetime = datetime.now(tz=timezone.utc)
    assert mock_pdi.session_exp < current_datetime
    assert mock_pdi.session_auth.expires
    assert mock_pdi.session_auth.expires < current_datetime
    assert mock_pdi.session_token == "AccessTokenExpired"
    assert mock_pdi.session_auth.api_key == "AccessTokenExpired"

    # Queue authentication response with new token, but do not load it into PDI
    requests_mock.post(
        "https://apiqa.bluevote.com/sessions",
        json={
            "AccessToken": "AccessTokenNew",
            "ExpirationDate": "2100-01-01",
        },
    )

    # Queue primary response
    request_url = "https://apiqa.bluevote.com"
    requests_mock.request(request_method, request_url)

    # Make primary request, causing token to also be refreshed
    mock_pdi._request(request_url, req_type=request_method)
    assert mock_pdi.session_exp > current_datetime
    assert mock_pdi.session_auth.expires
    assert mock_pdi.session_auth.expires > current_datetime
    assert mock_pdi.session_token == "AccessTokenNew"
    assert mock_pdi.session_auth.api_key == "AccessTokenNew"

    # Ensure that all requests after the first one include the new token
    history = requests_mock.request_history
    assert len(history) > 1
    for request in history[1:]:
        assert "Authorization" in request.headers
        assert request.headers["Authorization"] == "Bearer AccessTokenNew"
