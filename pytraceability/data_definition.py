from dataclasses import dataclass, field, asdict
from datetime import datetime

from pathlib import Path
from typing import Mapping, Any, Generator

MetaDataType = Mapping[str, Any]


@dataclass(eq=False)
class Traceability:
    key: str
    metadata: MetaDataType = field(default_factory=dict)
    is_complete: bool = True

    def __eq__(self, other: Any) -> bool:
        return self.key == other.key and self.metadata == other.metadata


@dataclass
class TraceabilityGitHistory:
    commit: str
    author_name: str | None
    author_date: datetime
    message: str
    source_code: str | None


@dataclass
class CurrentLocationRecord:
    file_path: Path
    function_name: str
    line_number: int
    end_line_number: int | None
    source_code: str | None


@dataclass
class TraceabilityReport(Traceability, CurrentLocationRecord):
    history: list[TraceabilityGitHistory] | None = None


@dataclass
class ExtractionResult(CurrentLocationRecord):
    traceability_data: list[Traceability]

    def is_complete(self) -> bool:
        return all(t.is_complete for t in self.traceability_data)


class ExtractionResultsList(list[ExtractionResult]):
    def _flat(self) -> Generator[TraceabilityReport, None, None]:
        for extraction_result in self:
            extraction_result_as_dict = asdict(extraction_result)
            extraction_result_as_dict.pop("traceability_data")
            for traceability_data in extraction_result.traceability_data:
                kwargs = asdict(traceability_data)
                kwargs.update(extraction_result_as_dict)
                yield TraceabilityReport(**kwargs)

    def flatten(self) -> list[TraceabilityReport]:
        return list(self._flat())
