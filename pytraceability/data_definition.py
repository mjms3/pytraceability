from dataclasses import dataclass, field

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
