"""Shared fixtures for dbt integration tests."""

from collections.abc import Callable
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from dbt.artifacts.resources.types import NodeType
from dbt.contracts.graph.manifest import ManifestMetadata
from dbt.contracts.results import (
    ExecutionResult,
    FreshnessStatus,
    NodeResult,
    NodeStatus,
    RunStatus,
    TestStatus,
)

from parsons.utilities.dbt.models import Manifest


@pytest.fixture
def build_manifest(dbt_node_factory, mock_manifest_data: Callable[..., ExecutionResult]):
    """
    Fixture helper to build a Parsons Manifest wrapper.

    Note: 'dbt_manifest' in the Parsons wrapper constructor actually expects a dbt ExecutionResult object.
    """

    def _maker(status=NodeStatus.Success, elapsed=10.0, cmd="run"):
        node = dbt_node_factory(status=status)
        execution_data = mock_manifest_data(results=[node])
        execution_data.elapsed_time = elapsed

        return Manifest(command=cmd, dbt_manifest=execution_data)

    return _maker


@pytest.fixture
def dbt_node_factory() -> Callable[..., NodeResult]:
    """
    Factory fixture for creating dbt NodeResult objects.

    Returns a callable that creates NodeResult instances using real dbt-core dataclasses.
    The inner 'node' object is mocked to simplify test setup while maintaining
    compatibility with dbt's API.

    Example:
        def test_something(dbt_node_factory):
            node = dbt_node_factory(status=RunStatus.Success, name="my_model")
            assert node.status == RunStatus.Success
    """

    def _create_node(
        status: RunStatus | TestStatus | FreshnessStatus = RunStatus.Success,
        name: str = "my_model",
        resource_type: NodeType = NodeType.Model,
        bytes_processed: int = 0,
    ) -> NodeResult:
        """Create a NodeResult object with specified parameters."""
        mock_node = MagicMock()
        mock_node.name = name
        mock_node.resource_type = resource_type

        return NodeResult(
            status=status,
            timing=[],
            thread_id="thread-1",
            execution_time=1.0,
            adapter_response={"bytes_processed": bytes_processed, "slot_ms": 3600000},
            message="Success",
            failures=None,
            node=mock_node,
        )

    return _create_node


@pytest.fixture
def mock_manifest_data() -> Callable[..., ExecutionResult]:
    """
    Factory fixture for creating dbt ExecutionResult objects with metadata.

    Returns a callable that creates ExecutionResult instances and manually attaches
    ManifestMetadata to simulate the structure expected by Parsons' Manifest wrapper.

    Note that ExecutionResult doesn't natively include metadata in its constructor,
    so we attach it post-instantiation.

    Example:
        def test_something(mock_manifest_data, dbt_node_factory):
            node = dbt_node_factory()
            execution = mock_manifest_data(results=[node])
            assert execution.metadata.project_id == "parsons_project"
    """

    def _create(results: list[NodeResult] | None = None) -> ExecutionResult:
        """Create an ExecutionResult with attached metadata."""
        result = ExecutionResult(
            results=results or [],
            elapsed_time=10.0,
        )

        result.metadata = ManifestMetadata(
            generated_at=datetime.strptime("2026-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            project_id="parsons_project",
        )

        return result

    return _create
