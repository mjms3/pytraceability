import fnmatch
from pathlib import Path
from typing import Generator

from pytraceability.ast_processing import extract_traceability_from_file_using_ast
from pytraceability.exceptions import (
    TraceabilityErrorMessages,
    InvalidTraceabilityError,
)
from pytraceability.custom import pytraceability
from pytraceability.data_definition import (
    ExtractionResult,
)
from pytraceability.config import PyTraceabilityMode, PyTraceabilityConfig
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
    info="If pytraceability can't extract data statically, it has the option "
    "to try to extract it dynamically by importing the module.",
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
        if config.mode == PyTraceabilityMode.static_only:
            raise InvalidTraceabilityError.from_allowed_message_types(
                TraceabilityErrorMessages.STATIC_MODE,
                f"The following nodes have dynamic data: {incomplete_extractions}",
            )
        elif config.mode == PyTraceabilityMode.static_plus_dynamic:
            yield from extract_traceabilities_using_module_import(
                file_path, project_root, incomplete_extractions
            )
        else:  # pragma: no cover
            raise ValueError(f"Invalid mode: {config.mode}")
