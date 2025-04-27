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
    Traceability,
    RawCode,
    TraceabilityReport,
)
from pytraceability.config import PROJECT_NAME

_log = logging.getLogger(__name__)


globals_ = {
    "datetime": datetime,
    "Decimal": Decimal,
}


class TraceabilityVisitor(ast.NodeVisitor):
    def __init__(self, decorator_name: str, file_path: Path, source_code: str) -> None:
        self.decorator_name = decorator_name
        self.file_path = file_path
        self.source_code = source_code

        self.stack = []
        self.extraction_results: list[TraceabilityReport] = []

    def visit(self, node):
        super().visit(node)
        return self.extraction_results

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
                return RawCode(code=source)

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
        num_args = len(decorator.args)
        if num_args > 1:
            raise InvalidTraceabilityError.from_allowed_message_types(
                TraceabilityErrorMessages.ONLY_ONE_ARG,
                f"Decorator has {num_args} args",
            )

        kwargs = {}
        for keyword in decorator.keywords:
            kwargs[keyword.arg] = self.walk_arg_definition(
                keyword.value, globals_=globals_
            )

        key_from_arg = (
            decorator.args[0].value
            if num_args == 1 and isinstance(decorator.args[0], ast.Constant)
            else None
        )
        key_from_kwarg = kwargs.pop("key", None)
        if key_from_arg and key_from_kwarg:
            raise InvalidTraceabilityError.from_allowed_message_types(
                TraceabilityErrorMessages.KEY_CAN_ONLY_BE_SPECIFIED_ONCE,
                f"Key is specified as both arg and kwarg: {key_from_arg} and {key_from_kwarg}",
            )
        if key_from_arg is None and key_from_kwarg is None:
            raise InvalidTraceabilityError.from_allowed_message_types(
                TraceabilityErrorMessages.KEY_MUST_BE_SPECIFIED
            )
        key = key_from_arg or key_from_kwarg

        if not isinstance(key, str):
            raise InvalidTraceabilityError.from_allowed_message_types(
                TraceabilityErrorMessages.KEY_MUST_BE_A_STRING,
            )

        _log.info(
            "Found traceability key: %s. metadata=%s",
            key,
            kwargs,
        )
        return Traceability(key=key, metadata=kwargs)

    def check_callable_node(self, node):
        for decorator in node.decorator_list:
            cast(ast.Call, decorator)
            if not hasattr(decorator, "func") or isinstance(
                decorator.func, ast.Attribute
            ):
                continue
            if decorator.func.id == self.decorator_name:
                traceability = self._extract_traceability_from_decorator(decorator)
                self.extraction_results.append(
                    TraceabilityReport(
                        file_path=self.file_path,
                        function_name=".".join(self.stack),
                        line_number=node.lineno,
                        end_line_number=node.end_lineno,
                        source_code=ast.get_source_segment(self.source_code, node),
                        key=traceability.key,
                        metadata=traceability.metadata,
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
    file_path: Path, decorator_name: str
) -> list[TraceabilityReport]:
    _log.info("Extracting traceability from file: %s", file_path)
    with open(file_path, "r") as f:
        source_code = f.read()
        try:
            tree = ast.parse(source_code, filename=file_path)
        except SyntaxError:
            _log.warning(f"Ignoring file due to syntax error: {file_path}")
            return []
        return TraceabilityVisitor(
            decorator_name, file_path=file_path, source_code=source_code
        ).visit(tree)
