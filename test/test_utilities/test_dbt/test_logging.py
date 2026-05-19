import re
from pathlib import Path
from typing import Any

import pytest
from dbt.contracts.results import NodeStatus

from parsons.utilities.dbt.logging import dbtLoggerMarkdown


class MarkdownLoggerTest(dbtLoggerMarkdown):
    """Test implementation of dbtLoggerMarkdown."""

    def send(self, manifests):
        pass


class TestMarkdownFormatting:
    """Consolidated suite for Markdown output and prioritization."""

    @pytest.mark.parametrize(
        ("status", "expected_icon"),
        [
            (NodeStatus.Success, "\U0001f7e2"),
            (NodeStatus.Error, "\U0001f534"),
            (NodeStatus.Fail, "\U0001f534"),
            (NodeStatus.Skipped, "\U0001f535"),
            (NodeStatus.Warn, "\U0001f7e0"),
        ],
    )
    def test_status_icon_mapping(self, status, expected_icon, build_manifest):
        """Verify icon mapping for individual command results."""
        manifest = build_manifest(status=status)
        output = MarkdownLoggerTest().format_command_result(manifest)
        assert expected_icon in output

    @pytest.mark.parametrize(
        ("statuses", "expected_icon", "expected_text", "expected_seconds"),
        [
            ([NodeStatus.Success, NodeStatus.Success], "\U0001f7e2", "succeeded", 20),
            ([NodeStatus.Success, NodeStatus.Fail], "\U0001f534", "failed", 20),
            ([NodeStatus.Error, NodeStatus.Warn], "\U0001f534", "failed", 20),
            ([NodeStatus.Warn, NodeStatus.Success], "\U0001f7e0", "succeeded with warnings", 20),
            ([NodeStatus.Skipped, NodeStatus.Success], "\U0001f535", "skipped", 20),
        ],
    )
    def test_overall_aggregation(
        self, statuses, expected_icon, expected_text, expected_seconds, build_manifest
    ):
        """Verify that the summary report correctly aggregates status and duration."""
        logger = MarkdownLoggerTest()
        logger.commands = [build_manifest(status=s, elapsed=10.0) for s in statuses]

        output = logger.format_result()
        header = output.split("\n")[0]

        assert expected_icon in header
        assert expected_text in header
        assert f"{expected_seconds} seconds" in output


class TestMarkdownInputValidation:
    """Test suite for input validation and error handling."""

    @pytest.mark.parametrize(
        "invalid_input",
        [
            Path(__file__),
            "Manifest",
            358762,
            NodeStatus.Error,
            [NodeStatus.Error, "Manifest"],
            ["Manifest", NodeStatus.Error],
        ],
    )
    def test_rejects_non_manifest_objects(self, invalid_input: Any):
        """Ensure clear TypeErrors when passing non-Manifest types."""
        logger = MarkdownLoggerTest()
        with pytest.raises(TypeError, match=re.escape(str(invalid_input))):
            logger._get_status_assets(manifest=invalid_input)  # type: ignore
