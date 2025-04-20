from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Any, Mapping

from pytraceability.data_definition import Traceability

MetaDataType = Mapping[str, Any]


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


STANDARD_DECORATOR_NAME = traceability.__name__


def file_is_excluded(path: Path, exclude_file_patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(str(path), pat) for pat in exclude_file_patterns)
