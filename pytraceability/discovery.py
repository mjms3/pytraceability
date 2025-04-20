from __future__ import annotations

import fnmatch
import logging
from itertools import groupby
from operator import attrgetter
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
    TraceabilityReport,
)
from pytraceability.history import get_line_based_history
from pytraceability.import_processing import extract_traceabilities_using_module_import

_log = logging.getLogger(__name__)


def _file_is_excluded(path: Path, exclude_file_patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(str(path), pat) for pat in exclude_file_patterns)


class PyTraceabilityCollector:
    def __init__(self, config: PyTraceabilityConfig) -> None:
        self.config = config

    @pytraceability(
        "PYTRACEABILITY-1",
        info=f"{PROJECT_NAME} searches a directory for traceability decorators",
    )
    def _get_file_paths(self) -> Generator[Path, None, None]:
        _log.info("Using exclude patterns %s", self.config.exclude_patterns)
        for file_path in self.config.base_directory.rglob("*.py"):
            if _file_is_excluded(file_path, self.config.exclude_patterns):
                _log.debug("Skipping %s", file_path)
                continue
            yield file_path

    @pytraceability(
        "PYTRACEABILITY-3",
        info=f"If {PROJECT_NAME} can't extract data statically, it has the option "
        "to try to extract it dynamically by importing the module.",
    )
    def collect(self) -> list[TraceabilityReport]:
        traceability_reports: dict[str, TraceabilityReport] = {}
        for file_path in self._get_file_paths():
            for report in extract_traceability_from_file_using_ast(
                file_path, self.config.decorator_name
            ):
                traceability_reports[report.key] = report

        incomplete_reports = [
            t for t in traceability_reports.values() if t.contains_raw_source_code
        ]
        _log.info(
            "%s traceability decorators contain raw source code.",
            len(incomplete_reports),
        )
        if (
            self.config.mode == PyTraceabilityMode.MODULE_IMPORT
            and len(incomplete_reports) > 0
        ):
            if self.config.python_root is None:  # pragma: no cover
                # Should never actually end up here, because the model_validator will
                # default this to base_directory, but we can't set it as non-optional
                # because it would break typing checking at model creation
                raise ValueError(
                    f"Python root directory must be set in {PyTraceabilityMode.MODULE_IMPORT} mode"
                )
            for file_path, traceabilities in groupby(
                incomplete_reports, attrgetter("file_path")
            ):
                for (
                    extracted_traceability
                ) in extract_traceabilities_using_module_import(
                    file_path, self.config.python_root, traceabilities
                ):
                    traceability_reports[
                        extracted_traceability.key
                    ].metadata = extracted_traceability.metadata

        if self.config.git_history_mode == GitHistoryMode.FUNCTION_HISTORY:
            _log.info("Collecting git history for traceability reports")
            git_histories = get_line_based_history(
                list(traceability_reports.values()), self.config
            )
            for traceability_key, git_history in git_histories.items():
                traceability_reports[traceability_key].history = git_history
        elif self.config.git_history_mode != GitHistoryMode.NONE:
            raise ValueError(
                f"Unsupported git history mode: {self.config.git_history_mode}"
            )
        return list(traceability_reports.values())
