from importlib import util
from pathlib import Path

from pytraceability.common import Traceability


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


def _extract_traceability_using_module_import(
    file_path: Path,
    project_root: Path,
    node_name: str,
) -> Traceability:
    module = _load_python_module(file_path, project_root)
    return getattr(module, node_name).__traceability__
