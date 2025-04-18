from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Mapping, Any, Generator, List

from pydantic import BaseModel, Field, computed_field


MetaDataType = Mapping[str, Any]


class RawCode:
    def __init__(self, code: str | None):
        self.code = code

    def __repr__(self):
        return f"{self.__class__.__name__}({self.code!r})"

    def __eq__(self, other):
        return self.code == other.code

    def __hash__(self):
        return hash(self.code)


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
    def is_complete(self) -> bool:
        return not self._contains_raw_source_code(self.metadata)


class TraceabilityGitHistory(BaseModel):
    commit: str
    author_name: str | None
    author_date: datetime
    message: str
    source_code: str | None


class CurrentLocationRecord(BaseModel):
    file_path: Path
    function_name: str
    line_number: int
    end_line_number: int | None
    source_code: str | None


class TraceabilityReport(Traceability, CurrentLocationRecord):
    history: list[TraceabilityGitHistory] | None = None


class ExtractionResult(CurrentLocationRecord):
    traceability_data: list[Traceability]


class ExtractionResultsList(List[ExtractionResult]):
    def _flat(self) -> Generator[TraceabilityReport, None, None]:
        for extraction_result in self:
            extraction_result_as_dict = extraction_result.model_dump()
            extraction_result_as_dict.pop("traceability_data")
            for traceability_data in extraction_result.traceability_data:
                kwargs = traceability_data.model_dump()
                kwargs.update(extraction_result_as_dict)
                yield TraceabilityReport(**kwargs)

    def flatten(self) -> list[TraceabilityReport]:
        return list(self._flat())
