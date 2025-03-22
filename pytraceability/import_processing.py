from dataclasses import replace
from importlib import util
from pathlib import Path
from typing import Generator

from pytraceability.common import Traceability, UNKNOWN, InvalidTraceabilityError
from pytraceability.data_definition import ExtractionResult


def _get_module_name(
    file_path: Path,
    project_root: Path,
) -> str:
    file_path = file_path.resolve()
    project_root = project_root.resolve()

    relative_path = file_path.relative_to(project_root)
    module_name = relative_path.with_suffix("").as_posix().replace("/", ".")
    if module_name.endswith("__init__"):
        module_name = module_name[:9]
    return module_name


def _load_python_module(
    file_path: Path,
    project_root: Path,
):
    module_name = _get_module_name(file_path, project_root)
    spec = util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(
            f"Unable to load spec for module: {module_name} from {file_path}"
        )
    module = util.module_from_spec(spec)
    if module is None:
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
            if any(t.key == UNKNOWN for t in extraction.traceability_data):
                raise InvalidTraceabilityError("Traceability key must be determinable")
            yield extraction
