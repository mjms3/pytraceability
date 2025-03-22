from dataclasses import replace
from importlib import util
from pathlib import Path
from typing import Generator

from pytraceability.common import (
    Traceability,
    UNKNOWN,
    InvalidTraceabilityError,
    TraceabilityErrorMessages,
)
from pytraceability.custom import pytraceability
from pytraceability.data_definition import ExtractionResult


def _get_module_name(
    file_path: Path,
    project_root: Path,
) -> str:
    file_path = file_path.resolve()
    project_root = project_root.resolve()

    relative_path = file_path.relative_to(project_root)
    return relative_path.with_suffix("").as_posix().replace("/", ".")


def _load_python_module(
    file_path: Path,
    project_root: Path,
):
    module_name = _get_module_name(file_path, project_root)
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


def _extract_traceability(module, node_name) -> list[Traceability]:
    current_top_level_object = module
    attribute_path_to_node = node_name.split(".")
    for attribute in attribute_path_to_node[:-1]:
        current_top_level_object = getattr(current_top_level_object, attribute)
    return getattr(
        current_top_level_object, attribute_path_to_node[-1]
    ).__traceability__


@pytraceability(
    "PYTRACEABILITY-4",
    info="If pytraceability can't extract the key either statically or dynamically, an"
    f"{InvalidTraceabilityError.__name__} is raised. This might happen for a closure where "
    "the traceability key is stored in a variable.",
)
def extract_traceabilities_using_module_import(
    file_path: Path,
    project_root: Path,
    extraction_results: list[ExtractionResult],
) -> Generator[ExtractionResult, None, None]:
    module = _load_python_module(file_path, project_root)
    for extraction in extraction_results:
        try:
            traceability_data = _extract_traceability(module, extraction.function_name)
            yield replace(extraction, traceability_data=traceability_data)
        except AttributeError:
            unknown_keys = (t.key == UNKNOWN for t in extraction.traceability_data)
            if any(unknown_keys):
                raise InvalidTraceabilityError.from_allowed_message_types(
                    TraceabilityErrorMessages.KEY_CAN_NOT_BE_UNKNOWN,
                    f"The traceability decorators with unknown keys are: {unknown_keys}",
                )
            yield extraction
