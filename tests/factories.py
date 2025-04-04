from pathlib import Path
from types import ModuleType
from unittest import mock

from pytraceability.config import (
    PyTraceabilityConfig,
    PyTraceabilityMode,
    get_repo_root,
)
from pytraceability.data_definition import (
    MetaDataType,
    TraceabilityGitHistory,
    TraceabilityReport,
)
from pytraceability.discovery import extract_traceability_from_file

TEST_ROOT = Path(__file__).parent
THIS_REPO_ROOT = get_repo_root(TEST_ROOT)
TEST_CONFIG = PyTraceabilityConfig(
    repo_root=THIS_REPO_ROOT,
    mode=PyTraceabilityMode.static_plus_dynamic,
)


def _test_from_module(
    module: ModuleType,
    function_name: str = "foo",
    line_num_offset: int = 0,
    metadata: MetaDataType | None = None,
    is_complete: bool = True,
    config: PyTraceabilityConfig = TEST_CONFIG,
    history: list[TraceabilityGitHistory] | None = None,
) -> None:
    if module.__file__ is None:
        raise ValueError(f"module.__file__ is None. Module: {module}")
    file_path = Path(module.__file__)
    actual = list(extract_traceability_from_file(file_path, TEST_ROOT, config))
    expected = [
        TraceabilityReport(
            file_path=file_path,
            function_name=function_name,
            line_number=5 + line_num_offset,
            end_line_number=6 + line_num_offset,
            source_code=mock.ANY,
            key="A key",
            metadata=metadata or {},
            is_complete=is_complete,
            history=history,
        ),
    ]
    assert actual == expected
