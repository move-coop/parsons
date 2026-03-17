from collections.abc import Callable
from datetime import datetime

import pytest
from dbt.artifacts.resources.types import NodeType
from dbt.artifacts.schemas.manifest import ManifestMetadata
from dbt.artifacts.schemas.results import NodeResult
from dbt.artifacts.schemas.run import RunExecutionResult
from dbt.contracts.results import NodeStatus

from parsons.utilities.dbt.models import Manifest


class TestManifestDataProcessing:
    """Test suite for Manifest data processing and computed properties."""

    @pytest.mark.parametrize(
        ("byte_counts", "expected_gb"),
        [([2 * 10**9], 2.0), ([1.5 * 10**9, 2.5 * 10**9], 4.0), ([], 0.0)],
    )
    def test_total_gb_processed(
        self,
        dbt_node_factory: Callable[..., NodeResult],
        run_execution_result_factory: Callable[..., RunExecutionResult],
        byte_counts: list[int | float],
        expected_gb: float,
    ):
        """Verify byte-to-GB conversion and summation across multiple nodes."""
        nodes = [dbt_node_factory(bytes_processed=b) for b in byte_counts]
        dbt_obj = run_execution_result_factory(nodes)
        manifest = Manifest(command="run", run_execution_result=dbt_obj)

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
    def test_summary_counts(
        self,
        dbt_node_factory: Callable[..., NodeResult],
        run_execution_result_factory: Callable[..., RunExecutionResult],
        statuses: list[NodeStatus],
        expected_counts: dict[NodeStatus, int],
    ):
        """Verify summary property correctly aggregates nodes by status."""
        nodes = [dbt_node_factory(status=s) for s in statuses]
        dbt_obj = run_execution_result_factory(nodes)
        manifest = Manifest(command="run", run_execution_result=dbt_obj)

        for status, count in expected_counts.items():
            assert manifest.summary[status] == count

    @pytest.mark.parametrize(
        ("statuses", "expected_overall"),
        [
            ([NodeStatus.Success, NodeStatus.Success], NodeStatus.Success),
            ([NodeStatus.Success, NodeStatus.Warn], NodeStatus.Warn),
            ([NodeStatus.Success, NodeStatus.Fail], NodeStatus.Error),
            ([NodeStatus.Error, NodeStatus.Warn], NodeStatus.Error),
            ([NodeStatus.Skipped], NodeStatus.Skipped),
            ([NodeStatus.Skipped, NodeStatus.Success], NodeStatus.Success),
        ],
    )
    def test_overall_status_precedence(
        self,
        dbt_node_factory: Callable[..., NodeResult],
        run_execution_result_factory: Callable[..., RunExecutionResult],
        statuses: list[NodeStatus],
        expected_overall: NodeStatus,
    ):
        """Verify that overall_status correctly prioritizes different node outcomes."""
        nodes = [dbt_node_factory(status=s) for s in statuses]
        manifest = Manifest(command="run", run_execution_result=run_execution_result_factory(nodes))
        assert manifest.overall_status == expected_overall


class TestManifestFiltering:
    """Test suite for Manifest filtering methods (skips, failures, etc.)."""

    def test_skips_filters_models_only(
        self,
        dbt_node_factory: Callable[..., NodeResult],
        run_execution_result_factory: Callable[..., RunExecutionResult],
    ):
        """Verify skips only includes skipped Models (ignoring Tests or Successes)."""
        nodes = [
            dbt_node_factory(status=NodeStatus.Skipped, name="m1", resource_type=NodeType.Model),
            dbt_node_factory(status=NodeStatus.Skipped, name="t1", resource_type=NodeType.Test),
            dbt_node_factory(status=NodeStatus.Success, name="m2", resource_type=NodeType.Model),
        ]
        manifest = Manifest(command="run", run_execution_result=run_execution_result_factory(nodes))

        assert len(manifest.skips) == 1
        assert manifest.skips[0].node.name == "m1"


class TestManifestAttributeAccess:
    """Test suite for Manifest's __getattr__ proxy behavior."""

    def test_getattr_hierarchy(self, dbt_node_factory):
        dbt_obj = RunExecutionResult(
            results=[dbt_node_factory()],
            args={"quiet": True},
            elapsed_time=1.23,
            generated_at=datetime.now(),
        )
        dbt_obj.metadata = ManifestMetadata(project_name="my_proj", dbt_version="1.7.0")

        manifest = Manifest(command="run", run_execution_result=dbt_obj)

        # Attributes in Manifest
        assert manifest.command == "run"
        # Attributes in ManifestMetadata
        assert manifest.dbt_version == "1.7.0"
        assert manifest.project_name == "my_proj"
        # Attributes in RunExecutionResult
        assert manifest.args["quiet"] is True
        assert manifest.elapsed_time == 1.23

    def test_getattr_missing_metadata(
        self, run_execution_result_factory: Callable[..., RunExecutionResult]
    ):
        """Verify fallback works even if the metadata attribute is missing entirely."""
        dbt_obj = run_execution_result_factory()

        if hasattr(dbt_obj, "metadata"):
            delattr(dbt_obj, "metadata")

        dbt_obj.custom_field = "test_value"
        manifest = Manifest(command="test", run_execution_result=dbt_obj)

        assert manifest.custom_field == "test_value"

        with pytest.raises(
            AttributeError, match="'Manifest' object has no attribute 'missing_key'"
        ):
            _ = manifest.missing_key
