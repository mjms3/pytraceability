from __future__ import annotations

import ast
import datetime
import logging
from decimal import Decimal
from pathlib import Path

from typing_extensions import cast

from pytraceability.exceptions import (
    TraceabilityErrorMessages,
    InvalidTraceabilityError,
)
from pytraceability.custom import pytraceability
from pytraceability.data_definition import (
    ExtractionResult,
    Traceability,
    RawCode,
)
from pytraceability.config import PyTraceabilityConfig, PROJECT_NAME

_log = logging.getLogger(__name__)


globals_ = {
    "datetime": datetime,
    "Decimal": Decimal,
}


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

    def safe_eval(self, node, globals_=None):
        try:
            return ast.literal_eval(node)
        except Exception as e:
            _log.debug(f"literal_eval failed for node: {ast.dump(node)} — {e}")
            try:
                code = compile(ast.Expression(body=node), "<ast>", "eval")
                return eval(code, globals_ or {}, {})
            except Exception as e2:
                source = ast.get_source_segment(self.source_code, node)
                _log.debug(f"eval failed for node: {source} — {e2}")
                return RawCode(source)

    def walk_arg_definition(self, node, globals_=None):
        if isinstance(node, ast.Dict):
            return {
                self.walk_arg_definition(k, globals_): self.walk_arg_definition(
                    v, globals_
                )
                for k, v in zip(node.keys, node.values)
            }
        elif isinstance(node, ast.List):
            return [self.walk_arg_definition(e, globals_) for e in node.elts]
        elif isinstance(node, ast.Tuple):
            return tuple(self.walk_arg_definition(e, globals_) for e in node.elts)
        elif isinstance(node, ast.Set):
            return set(self.walk_arg_definition(e, globals_) for e in node.elts)
        else:
            return self.safe_eval(node, globals_)

    def _extract_traceability_from_decorator(self, decorator: ast.Call) -> Traceability:
        kwargs = {}

        if not decorator.args:
            raise InvalidTraceabilityError.from_allowed_message_types(
                TraceabilityErrorMessages.KEY_MUST_BE_ARG
            )
        if len(decorator.args) != 1:
            raise InvalidTraceabilityError.from_allowed_message_types(
                TraceabilityErrorMessages.ONLY_ONE_ARG,
                f"Decorator has args: {[getattr(a, 's') or a for a in decorator.args]}",
            )
        if isinstance(decorator.args[0], ast.Constant):
            key = decorator.args[0].value
        else:
            raise InvalidTraceabilityError.from_allowed_message_types(
                TraceabilityErrorMessages.KEY_CAN_NOT_BE_DYNAMIC
            )

        for keyword in decorator.keywords:
            kwargs[keyword.arg] = self.walk_arg_definition(
                keyword.value, globals_=globals_
            )

        _log.info(
            "Found traceability key: %s. metadata=%s",
            key,
            kwargs,
        )
        return Traceability(key=key, metadata=kwargs)

    def check_callable_node(self, node):
        traceability = []
        for decorator in node.decorator_list:
            cast(ast.Call, decorator)
            if not hasattr(decorator, "func") or isinstance(
                decorator.func, ast.Attribute
            ):
                continue
            if decorator.func.id == self.config.decorator_name:
                traceability.append(
                    self._extract_traceability_from_decorator(decorator)
                )

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
            _log.debug("Processing %s: %s", node.__class__.__name__, name)
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
    _log.info("Extracting traceability from file: %s", file_path)
    with open(file_path, "r") as f:
        source_code = f.read()
        try:
            tree = ast.parse(source_code, filename=file_path)
        except SyntaxError:
            _log.warning(f"Ignoring file due to syntax error: {file_path}")
            return []
        return TraceabilityVisitor(
            config, file_path=file_path, source_code=source_code
        ).visit(tree)
