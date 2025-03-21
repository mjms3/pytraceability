import ast
from pathlib import Path
from typing import Generator

from pytraceability.common import (
    SearchResult,
    UNKNOWN,
    Traceability,
    ExtractionResult,
    PyTraceabilityConfig,
)


def _extract_traceability_from_decorator(decorator: ast.Call) -> SearchResult:
    kwargs = {}
    able_to_extract_statically = True

    if not decorator.args:
        raise ImportError("Expected a key as an arg")
    if isinstance(decorator.args[0], ast.Constant):
        key = decorator.args[0].s
    else:
        key = UNKNOWN
        able_to_extract_statically = False

    for keyword in decorator.keywords:
        if isinstance(keyword.value, ast.Constant):
            kwargs[keyword.arg] = keyword.value.s
        else:
            kwargs[keyword.arg] = UNKNOWN
            able_to_extract_statically = False

    return SearchResult(Traceability(key, kwargs), able_to_extract_statically)


def extract_traceability_from_file_using_ast(
    file_path: Path, config: PyTraceabilityConfig
) -> Generator[ExtractionResult, None, None]:
    with open(file_path, "r") as f:
        tree = ast.parse(f.read(), filename=file_path)
        yield from statically_extract_traceability_decorators(tree, config)


def statically_extract_traceability_decorators(
    tree: ast.Module, config: PyTraceabilityConfig
) -> Generator[ExtractionResult, None, None]:
    callable_nodes = (
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    )
    for node in callable_nodes:
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                raise RuntimeError(
                    f"Decorator {decorator} is not an instance of ast.Call"
                )
            if not isinstance(decorator.func, ast.Name):
                raise RuntimeError(
                    f"Decorator.func {decorator.func} s not an instance of ast.Name"
                )
            if decorator.func.id == config.decorator_name:
                ast_data = _extract_traceability_from_decorator(decorator)
                yield ExtractionResult(
                    function_name=node.name,
                    line_number=node.lineno,
                    end_line_number=node.end_lineno,
                    traceability_data=ast_data.traceability_data,
                    is_complete=ast_data.is_complete,
                )
