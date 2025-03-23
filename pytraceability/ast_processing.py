import ast
from pathlib import Path

from typing_extensions import cast

from pytraceability.common import (
    UNKNOWN,
)
from pytraceability.exceptions import (
    TraceabilityErrorMessages,
    InvalidTraceabilityError,
)
from pytraceability.custom import pytraceability
from pytraceability.data_definition import (
    ExtractionResult,
    Traceability,
)
from pytraceability.config import PyTraceabilityConfig, PROJECT_NAME


def _extract_traceability_from_decorator(decorator: ast.Call) -> Traceability:
    kwargs = {}
    able_to_extract_statically = True

    if not decorator.args:
        raise InvalidTraceabilityError.from_allowed_message_types(
            TraceabilityErrorMessages.KEY_MUST_BE_ARG
        )
    if len(decorator.args) != 1:
        raise InvalidTraceabilityError.from_allowed_message_types(
            TraceabilityErrorMessages.ONLY_ONE_ARG
        )
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

    return Traceability(key, kwargs, able_to_extract_statically)


class TraceabilityVisitor(ast.NodeVisitor):
    def __init__(
        self, config: PyTraceabilityConfig, file_path: Path, source_code: str
    ) -> None:
        self.config = config
        self.file_path = file_path
        self.source_code = source_code

        self.stack = []
        self.traceability_data: list[ExtractionResult] = []

    def visit(self, node):
        super().visit(node)
        return self.traceability_data

    def check_callable_node(self, node):
        traceability = []
        for decorator in node.decorator_list:
            cast(ast.Call, decorator)
            if not hasattr(decorator, "func") or isinstance(
                decorator.func, ast.Attribute
            ):
                continue
            if decorator.func.id == self.config.decorator_name:
                traceability.append(_extract_traceability_from_decorator(decorator))

        if len(traceability) > 0:
            self.traceability_data.append(
                ExtractionResult(
                    file_path=self.file_path,
                    function_name=".".join(self.stack),
                    line_number=node.lineno,
                    end_line_number=node.end_lineno,
                    source_code=ast.get_source_segment(self.source_code, node),
                    traceability_data=traceability,
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


@pytraceability(
    "PYTRACEABILITY-2",
    info=f"{PROJECT_NAME} extracts traceability info from the decorators statically",
)
def extract_traceability_from_file_using_ast(
    file_path: Path, config: PyTraceabilityConfig
) -> list[ExtractionResult]:
    with open(file_path, "r") as f:
        source_code = f.read()
        tree = ast.parse(source_code, filename=file_path)
        return TraceabilityVisitor(
            config, file_path=file_path, source_code=source_code
        ).visit(tree)
