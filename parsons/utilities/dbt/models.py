"""Pydantic data models for use with dbt utilities."""

from pydantic.v1 import BaseModel, Field, validator
import collections
from typing import Literal


class dbtResult(BaseModel):
    """For each dbt SQL operation, one dbtResult object is generated."""

    status: Literal["success", "pass", "warn", "error", "fail", "skipped"]
    execution_time: float
    node: str = Field(alias="unique_id")
    message: str | None = None
    bytes_processed: int | None = Field(default=None, alias="adapter_response")

    @validator("bytes_processed", pre=True)
    def unnest_bytes_processed(cls, value: dict) -> int | None:
        """Fetch bytes_processed from adapter_response"""
        return value.get("bytes_processed")


class dbtCommandResult(BaseModel):
    """Results from the execution of a dbt command.

    These results are fetched from the dbt-generated run_results.json
    file.
    """

    command: str
    elapsed_time: float
    results: list[dbtResult]

    def filter_results(self, **kwargs) -> list[dbtResult]:
        """Subset of results based on filter"""
        filtered_results = [
            result
            for result in self.results
            if all([getattr(result, key) == value for key, value in kwargs.items()])
        ]
        return filtered_results

    @property
    def warnings(self) -> list[dbtResult]:
        return self.filter_results(status="warn")

    @property
    def errors(self) -> list[dbtResult]:
        return self.filter_results(status="error")

    @property
    def skips(self) -> list[dbtResult]:
        return self.filter_results(status="skipped")

    @property
    def summary(self) -> collections.Counter:
        """Counts of pass, warn, fail, error & skip."""
        result = collections.Counter([i.status for i in self.results])
        return result
