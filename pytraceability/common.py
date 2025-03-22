from pytraceability.custom import pytraceability
from pytraceability.data_definition import Traceability, PyTraceabilityConfig


@pytraceability(
    "PYTRACEABILITY-1", info="Defines a traceability decorator @traceability"
)
def traceability(key: str, /, **kwargs):
    def wrapper(func):
        func.__traceability__ = Traceability(key, kwargs)
        return func

    return wrapper


DEFAULT_CONFIG = PyTraceabilityConfig()

UNKNOWN = "UNKNOWN"


class InvalidTraceabilityError(Exception):
    pass
