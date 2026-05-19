"""Shared fixtures for dbt integration tests."""

from collections.abc import Callable
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from dbt.artifacts.resources.types import NodeType
from dbt.artifacts.schemas.run import RunExecutionResult
from dbt.contracts.graph.manifest import ManifestMetadata
from dbt.contracts.graph.nodes import ResultNode
from dbt.contracts.results import (
    FreshnessStatus,
    NodeResult,
    NodeStatus,
    RunStatus,
    TestStatus,
)

from parsons.utilities.dbt.models import Manifest


@pytest.fixture
def run_execution_result_factory() -> Callable[[list[NodeResult] | None], RunExecutionResult]:
    """
    Factory fixture for creating dbt RunExecutionResult objects with metadata.

    Returns a callable that creates RunExecutionResult instances and manually attaches
    ManifestMetadata to simulate the structure expected by Parsons' Manifest wrapper.

    Note that RunExecutionResult doesn't natively include metadata in its constructor,
    so we attach it post-instantiation.

    .. code-block:: python

        def test_something(
            dbt_node_factory: Callable[..., NodeResult]
            run_execution_result_factory: Callable[..., RunExecutionResult],
        ):
            node = dbt_node_factory()
            execution = run_execution_result_factory([node])
            assert execution.metadata.project_id == "parsons_project"

    """

    def _create(results: list[NodeResult] | None = None) -> RunExecutionResult:
        """Create an RunExecutionResult with attached metadata."""
        result = RunExecutionResult(
            results=results or [],
            elapsed_time=10.0,
        )

        result.metadata = ManifestMetadata(
            generated_at=datetime.now(timezone.utc),
            project_id="parsons_project",
        )

        return result

    return _create


@pytest.fixture
def build_manifest(
    dbt_node_factory: Callable[..., NodeResult],
    run_execution_result_factory: Callable[..., RunExecutionResult],
) -> Callable[[RunStatus | TestStatus | FreshnessStatus, float, str], Manifest]:
    """Fixture helper to build a Parsons Manifest wrapper."""

    def _maker(
        status: RunStatus | TestStatus | FreshnessStatus = NodeStatus.Success,
        elapsed: float = 10.0,
        cmd: str = "run",
    ) -> Manifest:
        node = dbt_node_factory(status=status)
        execution_data = run_execution_result_factory([node])
        execution_data.elapsed_time = elapsed

        return Manifest(command=cmd, run_execution_result=execution_data)

    return _maker


@pytest.fixture
def dbt_node_factory() -> Callable[
    [RunStatus | TestStatus | FreshnessStatus, str, NodeType, int], NodeResult
]:
    """
    Factory fixture for creating dbt NodeResult objects.

    Returns a callable that creates NodeResult instances using real dbt-core dataclasses.
    The inner 'node' object is mocked to simplify test setup while maintaining
    compatibility with dbt's API.

    .. code-block:: python

        def test_something(dbt_node_factory):
            node = dbt_node_factory(status = RunStatus.Success, name = "my_model")
            assert node.status == RunStatus.Success

    """

    def _create_node(
        status: RunStatus | TestStatus | FreshnessStatus = RunStatus.Success,
        name: str = "my_model",
        resource_type: NodeType = NodeType.Model,
        bytes_processed: int = 0,
    ) -> NodeResult:
        """Create a NodeResult object with specified parameters."""
        mock_node = MagicMock(spec=ResultNode)
        mock_node.name = name
        mock_node.resource_type = resource_type
        mock_node.unique_id = f"{resource_type}.parsons.{name}"

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
