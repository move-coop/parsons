from unittest.mock import Mock

import pytest
from dbt.artifacts.resources.types import NodeType
from dbt.contracts.results import NodeStatus

from parsons.utilities.dbt.models import Manifest


class TestManifestDataProcessing:
    """Test suite for Manifest data processing and computed properties."""

    @pytest.mark.parametrize(
        ("byte_counts", "expected_gb"),
        [([2 * 10**9], 2.0), ([1.5 * 10**9, 2.5 * 10**9], 4.0), ([], 0.0)],
    )
    def test_total_gb_processed(
        self, dbt_node_factory, mock_manifest_data, byte_counts, expected_gb
    ):
        """Verify byte-to-GB conversion and summation across multiple nodes."""
        nodes = [dbt_node_factory(bytes_processed=b) for b in byte_counts]
        dbt_obj = mock_manifest_data(results=nodes)
        manifest = Manifest(command="run", dbt_manifest=dbt_obj)

        assert manifest.total_gb_processed == expected_gb

    @pytest.mark.parametrize(
        ("statuses", "expected_counts"),
        [
            ([NodeStatus.Success], {NodeStatus.Success: 1}),
            (
                [NodeStatus.Success, NodeStatus.Success, NodeStatus.Fail],
                {NodeStatus.Success: 2, NodeStatus.Fail: 1},
            ),
        ],
    )
    def test_summary_counts(self, dbt_node_factory, mock_manifest_data, statuses, expected_counts):
        """Verify summary property correctly aggregates nodes by status."""
        nodes = [dbt_node_factory(status=s) for s in statuses]
        dbt_obj = mock_manifest_data(results=nodes)
        manifest = Manifest(command="run", dbt_manifest=dbt_obj)

        for status, count in expected_counts.items():
            assert manifest.summary[status] == count


class TestManifestFiltering:
    """Test suite for Manifest filtering methods (skips, failures, etc.)."""

    def test_skips_filters_models_only(self, dbt_node_factory, mock_manifest_data):
        """Verify skips only includes skipped Models (ignoring Tests or Successes)."""
        nodes = [
            dbt_node_factory(status=NodeStatus.Skipped, name="m1", resource_type=NodeType.Model),
            dbt_node_factory(status=NodeStatus.Skipped, name="t1", resource_type=NodeType.Test),
            dbt_node_factory(status=NodeStatus.Success, name="m2", resource_type=NodeType.Model),
        ]
        manifest = Manifest(command="run", dbt_manifest=mock_manifest_data(results=nodes))

        assert len(manifest.skips) == 1
        assert manifest.skips[0].node.name == "m1"


class TestManifestAttributeAccess:
    """Test suite for Manifest's __getattr__ proxy behavior."""

    def test_getattr_hierarchy(self, mock_manifest_data):
        """
        Verify the attribute resolution order:
        1. Manifest Instance -> 2. dbt_manifest.metadata -> 3. dbt_manifest
        """
        dbt_obj = mock_manifest_data(results=[])
        dbt_obj.metadata = Mock(dbt_version="1.7.0", project_name="my_proj")
        dbt_obj.root_attr = "root_val"
        dbt_obj.command = "original_cmd"

        manifest = Manifest(command="override_cmd", dbt_manifest=dbt_obj)

        assert manifest.command == "override_cmd"
        assert manifest.dbt_version == "1.7.0"
        assert manifest.project_name == "my_proj"
        assert manifest.root_attr == "root_val"

    def test_getattr_missing_metadata(self, mock_manifest_data):
        """Verify fallback works even if the metadata attribute is missing entirely."""
        dbt_obj = mock_manifest_data(results=[])
        if hasattr(dbt_obj, "metadata"):
            delattr(dbt_obj, "metadata")

        dbt_obj.custom_field = "test_value"
