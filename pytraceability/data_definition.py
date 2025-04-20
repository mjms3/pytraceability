from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Mapping, Any

from pydantic import BaseModel, Field, computed_field


MetaDataType = Mapping[str, Any]


class RawCode(BaseModel):
    code: str | None


class Traceability(BaseModel):
    key: str
    metadata: MetaDataType = Field(default_factory=dict)

    @staticmethod
    def _contains_raw_source_code(value: Any) -> bool:
        if isinstance(value, RawCode):
            return True
        elif isinstance(value, (list, set, tuple)):
            return any(Traceability._contains_raw_source_code(item) for item in value)
        elif isinstance(value, dict):
            return any(
                Traceability._contains_raw_source_code(v) for v in value.values()
            )
        return False

    @computed_field
    @property
    def contains_raw_source_code(self) -> bool:
        return self._contains_raw_source_code(self.metadata)


class TraceabilityGitHistory(BaseModel):
    commit: str
    author_name: str | None
    author_date: datetime
    message: str
    source_code: str | None


class TraceabilityReport(Traceability):
    file_path: Path
    function_name: str
    line_number: int
    end_line_number: int | None
    source_code: str | None
    history: list[TraceabilityGitHistory] | None = None


class TraceabilitySummary(BaseModel):
    reports: list[TraceabilityReport]
