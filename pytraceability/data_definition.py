from dataclasses import dataclass, field
from enum import Enum

from pathlib import Path
from typing import Mapping, Any


MetaDataType = Mapping[str, Any]


@dataclass(frozen=True, eq=False)
class Traceability:
    key: str
    metadata: MetaDataType = field(default_factory=dict)
    is_complete: bool = True

    def __eq__(self, other: Any) -> bool:
        return self.key == other.key and self.metadata == other.metadata


class PyTraceabilityMode(str, Enum):
    static_only = "static-only"
    static_plus_dynamic = "static-plus-dynamic"


@dataclass(frozen=True)
class PyTraceabilityConfig:
    decorator_name: str = "traceability"
    exclude_patterns: list[str] = field(default_factory=lambda: [])
    mode: PyTraceabilityMode = PyTraceabilityMode.static_only


DEFAULT_CONFIG = PyTraceabilityConfig()


@dataclass
class ExtractionResult:
    file_path: Path
    function_name: str
    line_number: int
    end_line_number: int | None
    source_code: str | None
    traceability_data: list[Traceability]

    def is_complete(self) -> bool:
        return all(t.is_complete for t in self.traceability_data)
