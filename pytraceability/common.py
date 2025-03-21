from dataclasses import dataclass

MetaDataType = dict[str, str]


@dataclass
class Traceability:
    key: str
    metadata: MetaDataType | None = None


def traceability(key: str, /, **kwargs):
    def wrapper(func):
        func.__traceability__ = Traceability(key, kwargs)
        return func

    return wrapper


@dataclass(frozen=True)
class PyTraceabilityConfig:
    decorator_name: str = "traceability"


DEFAULT_CONFIG = PyTraceabilityConfig()


@dataclass
class SearchResult:
    traceability_data: Traceability
    is_complete: bool


@dataclass
class ExtractionResult(SearchResult):
    function_name: str
    line_number: int
    end_line_number: int | None


UNKNOWN = "UNKNOWN"


class InvalidTraceabilityError(Exception):
    pass
