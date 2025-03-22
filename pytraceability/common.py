from dataclasses import dataclass, field
from typing import Any, Mapping


MetaDataType = Mapping[str, Any]

UNKNOWN = "UNKNOWN"


class InvalidTraceabilityError(Exception):
    pass


class traceability:
    def __init__(self, key: str, /, **kwargs) -> None:
        self.key = key
        self.metadata = kwargs

    def __call__(self, fn):
        fn.__traceability__ = Traceability(key=self.key, metadata=self.metadata)
        return fn


@dataclass(frozen=True, eq=False)
class Traceability:
    key: str
    metadata: MetaDataType = field(default_factory=dict)

    def __eq__(self, other: Any) -> bool:
        return self.key == other.key and self.metadata == other.metadata
