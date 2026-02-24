"""Pydantic data models for use with dbt utilities."""

import collections
import warnings

from dbt.artifacts.resources.types import NodeType
from dbt.artifacts.schemas.run import RunExecutionResult
from dbt.contracts.results import NodeResult, NodeStatus, SourceFreshnessResult


class Manifest:
    """A wrapper for dbt execution results."""

    def __init__(
        self,
        command: str,
        run_execution_result: RunExecutionResult | None = None,
        *,
        dbt_manifest: RunExecutionResult | None = None,
    ) -> None:
        self.command = command
        self.run_execution_result = run_execution_result
        if self.run_execution_result is None and dbt_manifest is not None:
            self.run_execution_result = dbt_manifest
            warnings.warn(
                "dbt_manifest keyword is deprecated, use run_execution_result instead.",
                category=DeprecationWarning,
                stacklevel=2,
            )
        if self.run_execution_result is None:
            raise Exception("missing run_execution_result")

    def __getattr__(self, key: str):
        res = self.__dict__.get("run_execution_result")
        metadata = getattr(res, "metadata", None)
        if metadata is not None and hasattr(metadata, key):
            return getattr(metadata, key)
        try:
            return getattr(res, key)
        except AttributeError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{key}'"
            ) from None

    def __dir__(self) -> list[str]:
        """Merge Manifest attributes with public RunExecutionResult and ManifestMetadata attributes."""
        attrs = set(super().__dir__())
        res = self.__dict__.get("run_execution_result")
        if res:
            attrs.update(attr for attr in dir(res) if not attr.startswith("_"))
            metadata = getattr(res, "metadata", None)
            if metadata:
                attrs.update(attr for attr in dir(metadata) if not attr.startswith("_"))
        return sorted(attrs)

    def filter_results(self, **kwargs) -> list[NodeResult]:
        """Subset of NodeResults based on filter."""
        filtered_results = [
            result
            for result in self.results
            if isinstance(result, NodeResult)
            and all(str(getattr(result, key)) == value for key, value in kwargs.items())
        ]
        return filtered_results

    @property
    def dbt_manifest(self) -> RunExecutionResult:
        """Legacy proxy to new attribute."""
        warnings.warn(
            "dbt_manifest attribute is deprecated, use run_execution_result instead.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return self.run_execution_result

    @property
    def overall_status(self) -> NodeStatus:
        """
        Determine the overall state of the command.

        Returns a member of the NodeStatus Enum: Error, Warn, Skipped, or Success.
        """
        if self.errors or self.fails:
            return NodeStatus.Error
        if self.warnings:
            return NodeStatus.Warn
        success_keys = (NodeStatus.Success, NodeStatus.Pass)
        has_success = any(self.summary.get(k, 0) > 0 for k in success_keys)
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
            result
            for result in self.filter_results(status=NodeStatus.Skipped)
            if getattr(result.node, "resource_type", None) == NodeType.Model
        ]

    @property
    def summary(self) -> collections.Counter:
        """Aggregates all node outcomes into a count of status strings."""
        return collections.Counter([NodeStatus(i.status) for i in self.results])

    @property
    def total_gb_processed(self) -> float:
        """Total GB processed by full dbt command run."""
        return (
            sum([node.adapter_response.get("bytes_processed", 0) for node in self.results])
            / 1000000000
        )

    @property
    def total_slot_hours(self) -> float:
        """Total slot hours used by full dbt command run."""
        return sum([node.adapter_response.get("slot_ms", 0) for node in self.results]) / 3600000


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
