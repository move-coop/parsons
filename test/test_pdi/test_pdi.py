import pytest

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
