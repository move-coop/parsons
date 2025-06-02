"""Pydantic data models for use with dbt utilities."""

import collections

from dbt.contracts.graph.manifest import Manifest as dbtManifest
from dbt.contracts.results import NodeResult, SourceFreshnessResult


class Manifest:
    def __init__(self, command: str, dbt_manifest: dbtManifest) -> None:
        self.command = command
        self.dbt_manifest = dbt_manifest

    def __getattr__(self, key):
        if key in dir(self):
            result = getattr(self, key)
        elif (
            getattr(self.dbt_manifest, "metadata", {})
            and key in self.dbt_manifest.metadata.__dict__
        ):
            result = getattr(self.dbt_manifest.metadata, key)
        else:
            result = getattr(self.dbt_manifest, key)
        return result

    def filter_results(self, **kwargs) -> list[NodeResult]:
        """Subset of results based on filter"""
        filtered_results = [
            result
            for result in self.dbt_manifest
            if all(str(getattr(result, key)) == value for key, value in kwargs.items())
        ]
        return filtered_results

    @property
    def warnings(self) -> list[NodeResult]:
        return self.filter_results(status="warn")

    @property
    def errors(self) -> list[NodeResult]:
        return self.filter_results(status="error")

    @property
    def fails(self) -> list[NodeResult]:
        return self.filter_results(status="fail")

    @property
    def skips(self) -> list[NodeResult]:
        """Returns skipped model builds but not skipped tests."""
        return [
            node
            for node in self.filter_results(status="skipped")
            if node.node.name.split(".")[0] == "model"
        ]

    @property
    def summary(self) -> collections.Counter:
        """Counts of pass, warn, fail, error & skip."""
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
