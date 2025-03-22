import fnmatch
from dataclasses import replace
from pathlib import Path
from typing import Generator

from pytraceability.ast_processing import extract_traceability_from_file_using_ast
from pytraceability.common import (
    UNKNOWN,
    InvalidTraceabilityError,
)
from pytraceability.custom import pytraceability
from pytraceability.data_definition import PyTraceabilityConfig, ExtractionResult
from pytraceability.import_processing import _extract_traceability_using_module_import


def _file_is_excluded(path: Path, exclude_file_patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(str(path), pat) for pat in exclude_file_patterns)


@pytraceability(
    "PYTRACEABILITY-1",
    info="pytraceability searches a directory for traceability decorators",
)
def collect_traceability_from_directory(
    dir_path: Path,
    project_root: Path,
    config: PyTraceabilityConfig,
) -> Generator[ExtractionResult, None, None]:
    for file_path in dir_path.rglob("*.py"):
        if _file_is_excluded(file_path, config.exclude_patterns):
            continue
        yield from extract_traceability_from_file(file_path, project_root, config)


def extract_traceability_from_file(
    file_path: Path,
    project_root: Path,
    config: PyTraceabilityConfig,
) -> Generator[ExtractionResult, None, None]:
    for search_result in extract_traceability_from_file_using_ast(file_path, config):
        if search_result.is_complete():
            yield search_result
        else:
            try:
                traceability_data = _extract_traceability_using_module_import(
                    file_path, project_root, search_result.function_name
                )

            except AttributeError:
                # We can't extract info for this dynamically eg because it's a closure
                traceability_data = search_result.traceability_data

            if any(t.key == UNKNOWN for t in traceability_data):
                raise InvalidTraceabilityError("Traceability key must be determinable")
            yield replace(
                search_result,
                traceability_data=traceability_data,
            )
