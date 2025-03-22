from dataclasses import dataclass, field
from typing import Any, Mapping

MetaDataType = Mapping[str, Any]

UNKNOWN = "UNKNOWN"


class InvalidTraceabilityError(Exception):
    pass


@dataclass(frozen=True, eq=False)
class Traceability:
    key: str
    metadata: MetaDataType = field(default_factory=dict)
    is_complete: bool = True

    def __eq__(self, other: Any) -> bool:
        return self.key == other.key and self.metadata == other.metadata


class traceability:
    def __init__(self, key: str, /, **kwargs) -> None:
        self.key = key
        self.metadata = kwargs

    def __call__(self, fn):
        if not hasattr(fn, "__traceability__"):
            fn.__traceability__ = []
        if self.key in {t.key for t in fn.__traceability__}:
            raise ValueError(
                f"{self.key} appears more than once on decorators for {fn.__name__}"
            )
        fn.__traceability__.append(Traceability(key=self.key, metadata=self.metadata))
        return fn
