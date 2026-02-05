"""Pydantic data models for use with dbt utilities."""

import collections

from dbt.artifacts.resources.types import NodeType
from dbt.contracts.results import ExecutionResult, NodeResult, NodeStatus, SourceFreshnessResult


class Manifest:
    """A wrapper for dbt execution results."""

    def __init__(self, command: str, dbt_manifest: ExecutionResult) -> None:
        self.command = command
        self.dbt_manifest = dbt_manifest

    def __getattr__(self, key: str):
        """Proxies attribute access to the underlying dbt_manifest or its metadata."""
        metadata = getattr(self.dbt_manifest, "metadata", None)
        if metadata is not None and key in getattr(metadata, "__dict__", {}):
            return getattr(metadata, key)

        try:
            return getattr(self.dbt_manifest, key)
        except AttributeError as e:
            error_msg = f"'{type(self).__name__}' object has no attribute '{key}'"
            raise AttributeError(error_msg) from e

    def filter_results(self, **kwargs) -> list[NodeResult]:
        """Subset of results based on filter."""
        filtered_results = [
            result
            for result in self.dbt_manifest
            if all(str(getattr(result, key)) == value for key, value in kwargs.items())
        ]
        return filtered_results

    @property
    def overall_status(self) -> str:
        """
        Determine the overall state of the command.

        Returns a member of the NodeStatus Enum: Error, Warn, Skipped, or Success.
        """
        if self.errors or self.fails:
            return NodeStatus.Error
        if self.warnings:
            return NodeStatus.Warn

        has_success = (
            self.summary.get(NodeStatus.Success, 0) > 0 or self.summary.get(NodeStatus.Pass, 0) > 0
        )
        if self.skips and not has_success:
            return NodeStatus.Skipped

        return NodeStatus.Success

    @property
    def warnings(self) -> list[NodeResult]:
        return self.filter_results(status=NodeStatus.Warn)

    @property
    def errors(self) -> list[NodeResult]:
        return self.filter_results(status=NodeStatus.Error)

    @property
    def fails(self) -> list[NodeResult]:
        return self.filter_results(status=NodeStatus.Fail)

    @property
    def skips(self) -> list[NodeResult]:
        """Returns skipped model builds but not skipped tests."""
        return [
            node
            for node in self.filter_results(status=NodeStatus.Skipped)
            if getattr(node.node, "resource_type", None) == NodeType.Model
        ]

    @property
    def summary(self) -> collections.Counter:
        """Aggregates all node outcomes into a count of status strings."""
        result = collections.Counter([str(i.status) for i in self.dbt_manifest])
        return result

    @property
    def total_gb_processed(self) -> float:
        """Total GB processed by full dbt command run."""
        result = (
            sum([node.adapter_response.get("bytes_processed", 0) for node in self.dbt_manifest])
            / 1000000000
        )
        return result

    @property
    def total_slot_hours(self) -> float:
        """Total slot hours used by full dbt command run."""
        result = (
            sum([node.adapter_response.get("slot_ms", 0) for node in self.dbt_manifest]) / 3600000
        )
        return result


class EnhancedNodeResult(NodeResult):
    def log_message(self) -> str | None:
        """Helper method to generate message for logs."""
        if isinstance(self, SourceFreshnessResult):
            freshness_config = self.node.freshness
            time_config = getattr(freshness_config, self.status + "_after")
            result = f"No new records for {int(self.age / 86400)} days, {self.status} after {time_config.count} {time_config.period}s."
        else:
            result = self.message

        return result
