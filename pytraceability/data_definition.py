from dataclasses import dataclass, field
from typing import Mapping, Any

MetaDataType = Mapping[str, Any]


@dataclass
class Traceability:
    key: str
    metadata: MetaDataType = field(default_factory=dict)


@dataclass(frozen=True)
class PyTraceabilityConfig:
    decorator_name: str = "traceability"
    exclude_patterns: list[str] = field(default_factory=lambda: [])


@dataclass
class SearchResult:
    traceability_data: Traceability
    is_complete: bool


@dataclass
class ExtractionResult(SearchResult):
    function_name: str
    line_number: int
    end_line_number: int | None
