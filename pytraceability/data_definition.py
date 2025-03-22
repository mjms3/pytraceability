from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Any

from pytraceability.common import Traceability

MetaDataType = Mapping[str, Any]


@dataclass(frozen=True)
class PyTraceabilityConfig:
    decorator_name: str = "traceability"
    exclude_patterns: list[str] = field(default_factory=lambda: [])


DEFAULT_CONFIG = PyTraceabilityConfig()


@dataclass
class ExtractionResult:
    file_path: Path
    function_name: str
    line_number: int
    end_line_number: int | None
    traceability_data: list[Traceability]

    def is_complete(self) -> bool:
        return all(t.is_complete for t in self.traceability_data)
