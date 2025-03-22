import ast
from pathlib import Path

from pytraceability.common import (
    UNKNOWN,
    Traceability,
)
from pytraceability.data_definition import (
    PyTraceabilityConfig,
    SearchResult,
    ExtractionResult,
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


class Visitor(ast.NodeVisitor):
    def __init__(self, config: PyTraceabilityConfig) -> None:
        self.stack = []
        self.traceability_data: list[ExtractionResult] = []
        self.config = config

    def visit(self, node):
        super().visit(node)
        return self.traceability_data

    def check_callable_node(self, node):
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            if not isinstance(decorator.func, ast.Name):
                continue
            if decorator.func.id == self.config.decorator_name:
                ast_data = _extract_traceability_from_decorator(decorator)
                self.traceability_data.append(
                    ExtractionResult(
                        function_name=".".join(self.stack),
                        line_number=node.lineno,
                        end_line_number=node.end_lineno,
                        traceability_data=ast_data.traceability_data,
                        is_complete=ast_data.is_complete,
                    )
                )

    def generic_visit(self, node):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            name = node.name
            self.stack.append(name)
            self.check_callable_node(node)
            super().generic_visit(node)
            self.stack.pop()
        else:
            super().generic_visit(node)


def extract_traceability_from_file_using_ast(
    file_path: Path, config: PyTraceabilityConfig
) -> list[ExtractionResult]:
    with open(file_path, "r") as f:
        tree = ast.parse(f.read(), filename=file_path)
        return Visitor(config).visit(tree)
