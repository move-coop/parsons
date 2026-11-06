"""Test telemetry functionality."""

import importlib.metadata
from uuid import RFC_4122, UUID

import pytest
from posthog import Posthog

from parsons.telemetry import check_telemetry_enabled, configure_telemetry


@pytest.mark.parametrize(
    ("env_variables", "expected"),
    [
        ([("PYTEST_VERSION", None), ("PARSONS_TELEMETRY", "false")], False),
        ([("PYTEST_VERSION", None), ("PARSONS_TELEMETRY", "true")], True),
        ([("PYTEST_VERSION", None), ("PARSONS_TELEMETRY", None)], True),
        ([("PYTEST_VERSION", "9.0.2"), ("PARSONS_TELEMETRY", "true")], False),
        ([("PYTEST_VERSION", "9.0.2"), ("PARSONS_TELEMETRY", "false")], False),
    ],
    ids=["opt-out", "opt-in", "default", "pytest-with-opt-in", "pytest-with-opt-out"],
)
def test_telemetry_enabled(
    monkeypatch: pytest.MonkeyPatch, env_variables: list[tuple[str, str | None]], *, expected: bool
) -> None:
    """Test telemetry enable/disable logic, including warning when enabled."""
    for key, val in env_variables:
        if val is not None:
            monkeypatch.setenv(key, val, prepend=None)
        else:
            monkeypatch.delenv(key, raising=False)

    if expected:
        with pytest.warns(RuntimeWarning, match="Parsons telemetry is enabled"):
            assert check_telemetry_enabled() == expected
    else:
        assert check_telemetry_enabled() == expected


@pytest.mark.parametrize(
    ("invert_path_logic", "version_string"),
    [
        (True, importlib.metadata.version("parsons")),
        (False, "git"),
    ],
    ids=["production", "development"],
)
def test_configure_telemetry(
    invert_path_logic: bool,
    version_string: str,
) -> None:
    """Test that telemetry configuration includes api key, correct uuid format, and expected parsons version info."""
    posthog, telemetry_id, parsons_version = configure_telemetry(invert_path_logic)

    assert isinstance(posthog, Posthog)
    assert isinstance(posthog.api_key, str)
    assert posthog.api_key.startswith("phc_")

    assert isinstance(telemetry_id, UUID)
    assert telemetry_id.variant == RFC_4122
    assert telemetry_id.version == 4

    assert isinstance(parsons_version, str)
    assert parsons_version == version_string
