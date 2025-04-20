from __future__ import annotations

import logging
from importlib import util
from pathlib import Path
from typing import Generator, Iterator

from pytraceability.common import (
    Traceability,
)
from pytraceability.config import PROJECT_NAME
from pytraceability.custom import pytraceability
from pytraceability.data_definition import (
    TraceabilityReport,
)
from pytraceability.exceptions import (
    InvalidTraceabilityError,
)

_log = logging.getLogger(__name__)


def _get_module_name(
    file_path: Path,
    python_root: Path,
) -> str:
    file_path = file_path.resolve()
    python_root = python_root.resolve()

    relative_path = file_path.relative_to(python_root)
    return relative_path.with_suffix("").as_posix().replace("/", ".")


def _load_python_module(
    file_path: Path,
    python_root: Path,
):
    module_name = _get_module_name(file_path, python_root)
    spec = util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise RuntimeError(
            f"Unable to load spec for module: {module_name} from {file_path}"
        )
    module = util.module_from_spec(spec)
    if module is None:  # pragma: no cover
        raise RuntimeError(f"Unable to load module from spec {spec}")
    spec.loader.exec_module(module)
    return module


def _extract_traceability(module, node_name) -> Generator[Traceability, None, None]:
    current_top_level_object = module
    attribute_path_to_node = node_name.split(".")
    for attribute in attribute_path_to_node[:-1]:
        current_top_level_object = getattr(current_top_level_object, attribute)
    if imported_callable := getattr(
        current_top_level_object, attribute_path_to_node[-1], None
    ):
        for traceability in imported_callable.__traceability__:
            yield traceability


@pytraceability(
    "PYTRACEABILITY-4",
    info=f"If {PROJECT_NAME} can't extract the key either statically or dynamically, an"
    f"{InvalidTraceabilityError.__name__} is raised. This might happen for a closure where "
    "the traceability key is stored in a variable.",
)
def extract_traceabilities_using_module_import(
    file_path: Path,
    python_root: Path,
    traceability_reports: Iterator[TraceabilityReport],
) -> Generator[Traceability, None, None]:
    _log.info("Extracting traceability from %s using module import", file_path)
    module = _load_python_module(file_path, python_root)
    for traceability_report in traceability_reports:
        yield from _extract_traceability(module, traceability_report.function_name)
