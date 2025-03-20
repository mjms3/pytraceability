import ast
from dataclasses import dataclass, replace
from importlib import util
from pathlib import Path
from typing import Generator


MetaDataType = dict[str, str]


@dataclass
class Traceability:
    key: str
    metadata: MetaDataType | None = None


def traceability(key: str, **kwargs):
    def wrapper(func):
        func.__traceability__ = Traceability(key, kwargs)
        return func

    return wrapper


@dataclass
class ExtractionResult:
    traceability_data: Traceability
    is_complete: bool


UNKNOWN = "UNKNOWN"


def _extract_traceability_from_decorator(decorator: ast.Call) -> ExtractionResult:
    key = UNKNOWN
    kwargs = {}
    able_to_extract_statically = True
    for keyword in decorator.keywords:
        if isinstance(keyword.value, ast.Constant):
            kwargs[keyword.arg] = keyword.value.s
        else:
            able_to_extract_statically = False

    if decorator.args:
        if isinstance(decorator.args[0], ast.Constant):
            key = decorator.args[0].s
        else:
            able_to_extract_statically = False

    if "key" in kwargs:
        key = kwargs.pop("key")
    return ExtractionResult(Traceability(key, kwargs), able_to_extract_statically)


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


@dataclass
class SearchResult(ExtractionResult):
    function_name: str
    line_number: int
    end_line_number: int | None


def _find_traceability_decorators(
    file_path: Path,
) -> Generator[SearchResult, None, None]:
    with open(file_path, "r") as f:
        tree = ast.parse(f.read(), filename=file_path)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for decorator in node.decorator_list:
                if not isinstance(decorator, ast.Call):
                    raise RuntimeError(
                        f"Decorator {decorator} is not an instance of ast.Call"
                    )
                if not isinstance(decorator.func, ast.Name):
                    raise RuntimeError(
                        f"Decorator.func {decorator.func} s not an instance of ast.Name"
                    )
                if decorator.func.id == traceability.__name__:
                    ast_data = _extract_traceability_from_decorator(decorator)
                    yield SearchResult(
                        function_name=node.name,
                        line_number=node.lineno,
                        end_line_number=node.end_lineno,
                        traceability_data=ast_data.traceability_data,
                        is_complete=ast_data.is_complete,
                    )


def collect_traceability_from_directory(
    dir_path: Path, project_root: Path
) -> Generator[SearchResult, None, None]:
    for file_path in dir_path.rglob("*.py"):
        yield from extract_traceability_from_file(file_path, project_root)


class InvalidTraceabilityError(Exception):
    pass


def extract_traceability_from_file(
    file_path: Path, project_root: Path
) -> Generator[SearchResult, None, None]:
    for search_result in _find_traceability_decorators(file_path):
        if search_result.is_complete:
            yield search_result
        else:
            try:
                traceability_data = _extract_traceability_using_module_import(
                    file_path, project_root, search_result.function_name
                )
                is_complete = True
            except AttributeError:
                # We can't extract info for this dynamically eg because it's a closure
                traceability_data = search_result.traceability_data
                is_complete = False
            if traceability_data.key == UNKNOWN:
                raise InvalidTraceabilityError("Traceability key must be determinable")
            yield replace(
                search_result,
                traceability_data=traceability_data,
                is_complete=is_complete,
            )
