import fnmatch
from pathlib import Path
from typing import Generator

from pytraceability.ast_processing import extract_traceability_from_file_using_ast
from pytraceability.custom import pytraceability
from pytraceability.data_definition import PyTraceabilityConfig, ExtractionResult
from pytraceability.import_processing import extract_traceabilities_using_module_import


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


@pytraceability(
    "PYTRACEABILITY-3",
    info="if pytraceability can't extract data statically, it tries to extract it dynamically by importing the module",
)
def extract_traceability_from_file(
    file_path: Path,
    project_root: Path,
    config: PyTraceabilityConfig,
) -> Generator[ExtractionResult, None, None]:
    incomplete_extractions = []
    for extraction in extract_traceability_from_file_using_ast(file_path, config):
        if extraction.is_complete():
            yield extraction
        else:
            incomplete_extractions.append(extraction)
    if len(incomplete_extractions) > 0:
        yield from extract_traceabilities_using_module_import(
            file_path, project_root, incomplete_extractions
        )
