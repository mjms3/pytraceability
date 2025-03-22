from typing import TypedDict

from pytraceability.data_definition import Traceability
from typing_extensions import Unpack


class PyTraceabilityArgs(TypedDict):
    info: str


def pytraceability(key: str, /, **kwargs: Unpack[PyTraceabilityArgs]):
    def wrapper(func):
        func.__traceability__ = Traceability(key, metadata=kwargs)
        return func

    return wrapper
