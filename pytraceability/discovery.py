from __future__ import annotations

import fnmatch
import logging
from pathlib import Path
from typing import Generator

from pytraceability.ast_processing import extract_traceability_from_file_using_ast
from pytraceability.config import (
    PyTraceabilityMode,
    PyTraceabilityConfig,
    PROJECT_NAME,
    GitHistoryMode,
)
from pytraceability.custom import pytraceability
from pytraceability.data_definition import (
    ExtractionResultsList,
    TraceabilityReport,
)
from pytraceability.exceptions import (
    TraceabilityErrorMessages,
    InvalidTraceabilityError,
)
from pytraceability.history import get_line_based_history
from pytraceability.import_processing import extract_traceabilities_using_module_import

_log = logging.getLogger(__name__)


def _file_is_excluded(path: Path, exclude_file_patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(str(path), pat) for pat in exclude_file_patterns)


class PyTraceabilityCollector:
    def __init__(self, config: PyTraceabilityConfig) -> None:
        self.config = config

    def collect(self) -> Generator[TraceabilityReport, None, None]:
        return self.collect_output_data()

    @pytraceability(
        "PYTRACEABILITY-1",
        info=f"{PROJECT_NAME} searches a directory for traceability decorators",
    )
    def collect_output_data(self) -> Generator[TraceabilityReport, None, None]:
        traceability_reports = self.collect_traceability_from_directory()
        if self.config.git_history_mode == GitHistoryMode.NONE:
            yield from traceability_reports
        elif self.config.git_history_mode == GitHistoryMode.FUNCTION_HISTORY:
            _log.info("Collecting git history for traceability reports")
            traceability_report_list = list(traceability_reports)
            git_history = get_line_based_history(traceability_report_list, self.config)
            for report in traceability_report_list:
                report.history = git_history.get(report.key)
                yield report
        else:  # pragma: no cover
            raise ValueError(
                f"Unsupported git history mode: {self.config.git_history_mode}"
            )

    def collect_traceability_from_directory(
        self,
    ) -> Generator[TraceabilityReport, None, None]:
        _log.info("Using exclude patterns %s", self.config.exclude_patterns)
        for file_path in self.config.base_directory.rglob("*.py"):
            if _file_is_excluded(file_path, self.config.exclude_patterns):
                _log.debug("Skipping %s", file_path)
                continue
            yield from self.extract_traceability_from_file(file_path)

    @pytraceability(
        "PYTRACEABILITY-3",
        info=f"If {PROJECT_NAME} can't extract data statically, it has the option "
        "to try to extract it dynamically by importing the module.",
    )
    def extract_traceability_from_file(
        self,
        file_path: Path,
    ) -> list[TraceabilityReport]:
        extractions = ExtractionResultsList()
        incomplete_extractions = []
        for extraction in extract_traceability_from_file_using_ast(
            file_path, self.config.decorator_name
        ):
            if all(t.is_complete for t in extraction.traceability_data):
                extractions.append(extraction)
            else:
                incomplete_extractions.append(extraction)
        if len(incomplete_extractions) > 0:
            _log.info(
                "%s traceability decorators could not be extracted statically.",
                len(incomplete_extractions),
            )
            if self.config.mode == PyTraceabilityMode.STATIC_ONLY:
                raise InvalidTraceabilityError.from_allowed_message_types(
                    TraceabilityErrorMessages.STATIC_MODE,
                    f"The following nodes have dynamic data: {incomplete_extractions}",
                )
            elif self.config.mode == PyTraceabilityMode.ALLOW_RAW_SOURCE_CODE:
                _log.info('"Allowing raw source code to be used for traceability"')
                extractions.extend(incomplete_extractions)
            elif self.config.mode == PyTraceabilityMode.STATIC_PLUS_DYNAMIC:
                if self.config.python_root is None:  # pragma: no cover
                    # Should never actually end up here, because the model_validator will
                    # default this to base_directory, but we can't set it as non-optional
                    # because it would break typing checking at model creation
                    raise ValueError(
                        f"Python root directory must be set in {PyTraceabilityMode.STATIC_PLUS_DYNAMIC} mode"
                    )
                extractions.extend(
                    extract_traceabilities_using_module_import(
                        file_path, self.config.python_root, incomplete_extractions
                    )
                )
            else:  # pragma: no cover
                raise ValueError(f"Invalid mode: {self.config.mode}")
        return extractions.flatten()
