"""Pydantic data models for use with dbt utilities."""

import collections
from dbt.contracts.graph.manifest import Manifest as dbtManifest
from dbt.contracts.results import NodeResult


class Manifest:
    def __init__(self, command: str, dbt_manifest: dbtManifest) -> None:
        self.command = command
        self.dbt_manifest = dbt_manifest

    def __getattr__(self, key):
        if key in self.__dict__:
            result = self.__dict__[key]
        else:
            result = getattr(self.dbt_manifest, key)
        return result

    def filter_results(self, **kwargs) -> list[NodeResult]:
        """Subset of results based on filter"""
        filtered_results = [
            result
            for result in self.dbt_manifest
            if all([str(getattr(result, key)) == value for key, value in kwargs.items()])
        ]
        return filtered_results

    @property
    def warnings(self) -> list[NodeResult]:
        return self.filter_results(status="warn")

    @property
    def errors(self) -> list[NodeResult]:
        return self.filter_results(status="error")

    @property
    def skips(self) -> list[NodeResult]:
        return self.filter_results(status="skipped")

    @property
    def summary(self) -> collections.Counter:
        """Counts of pass, warn, fail, error & skip."""
        result = collections.Counter([str(i.status) for i in self.dbt_manifest])
        return result
