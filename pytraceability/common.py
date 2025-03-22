from typing import Any, Mapping

from pytraceability.data_definition import Traceability

MetaDataType = Mapping[str, Any]

UNKNOWN = "UNKNOWN"


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
