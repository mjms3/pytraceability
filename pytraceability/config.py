from dataclasses import dataclass, field
from enum import Enum


class PyTraceabilityMode(str, Enum):
    static_only = "static-only"
    static_plus_dynamic = "static-plus-dynamic"


@dataclass(frozen=True)
class PyTraceabilityConfig:
    decorator_name: str = "traceability"
    exclude_patterns: list[str] = field(default_factory=lambda: [])
    mode: PyTraceabilityMode = PyTraceabilityMode.static_only


DEFAULT_CONFIG = PyTraceabilityConfig()
