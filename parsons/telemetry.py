"""Telemetry handling for collecting basic information about parsons use."""

import importlib.metadata
import os
import pathlib
import warnings
from typing import Any
from uuid import UUID, uuid4

from posthog import Posthog


def check_telemetry_enabled() -> bool:
    """
    Determine if telemetry should be enabled.

    If enabled, inform users that they can opt-out by
    setting the PARSONS_TELEMETRY environment variable to 'false'.

    Returns:
        Whether telemetry is enabled.

    """
    if "PYTEST_VERSION" in os.environ:
        return False

    opt_out = os.environ.get("PARSONS_TELEMETRY", "true") != "true"

    if not opt_out:
        warnings.warn(
            (
                "Parsons telemetry is enabled. For more information, "
                "see <parsons telemetry documentation link here>. "
                "To opt-out, set your PARSONS_TELEMETRY environment variable to 'false'."
            ),  # TODO(bmos): document telemetry on website and add link
            category=RuntimeWarning,
            stacklevel=2,
        )

    return not opt_out


def configure_telemetry(
    invert_path_logic: bool = False,
) -> tuple[Posthog, UUID, str]:
    """
    Configure telemetry for the Parsons library.

    Args:
        invert_path_logic:
            If ``True``, inverts the logic for determining development mode.
            Defaults to ``False``. Used in testing.

    Returns:
        A tuple containing the Posthog client, telemetry UUID, and Parsons version.
        ``None`` if telemetry is disabled.

    """
    telemetry_id = uuid4()
    development_path_fragments = ["site-packages", "dist-packages"]
    init_path = pathlib.Path(__file__).resolve()
    development_mode = not any(p in init_path.parts for p in development_path_fragments)
    if invert_path_logic:
        development_mode = not development_mode
    parsons_version = importlib.metadata.version("parsons") if not development_mode else "git"

    posthog = Posthog(
        project_api_key="phc_AdyQBW8eUMQAmPFBtgngXHe8WawYAqUXoYdhnH6hM3Qq",
        host="https://us.i.posthog.com",
        before_send=lambda event: (event.pop("ip", None), event)[1],
    )

    return posthog, telemetry_id, parsons_version


def submit_telemetry(
    posthog: Posthog,
    event_name: str,
    telemetry_uuid: UUID,
    *,
    parsons_version: str | None = None,
    properties: dict[str, Any] | None = None,
) -> None:
    """
    Submit telemetry data to Posthog.

    Includes parsons version and provided properties

    Args:
        posthog:
            The Posthog client.
        telemetry_id:
            The UUID to associate with the event.
        parsons_version:
            The version of Parsons to include in the telemetry event data.
        properties:
            Additional properties to include in the telemetry event data.

    """
    telemetry_properties = {}
    if parsons_version:
        telemetry_properties["$parsons_version"] = parsons_version
    if properties:
        telemetry_properties.update(properties)
    posthog.capture(
        event_name,
        distinct_id=telemetry_uuid,
        properties=telemetry_properties,
    )
