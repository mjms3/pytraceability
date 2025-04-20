from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest
from git import Repo
from pydantic import BaseModel

from pytraceability.config import GitHistoryMode, PyTraceabilityConfig
from pytraceability.data_definition import TraceabilityGitHistory
from pytraceability.collector import PyTraceabilityCollector
from tests.utils import M

GIT_HISTORY_TESTS_DIR = Path(__file__).parent / "git_history_tests"


ADD_NEW_DECORATOR = "add new decorator"
DECORATOR_FUNCTION_RENAMED = "decorator function renamed"
DECORATOR_MOVED_TO_ANOTHER_FILE = "decorator moved to another file"


@pytest.fixture()
def config(tmp_path: Path) -> PyTraceabilityConfig:
    return PyTraceabilityConfig(
        base_directory=tmp_path,
        git_history_mode=GitHistoryMode.FUNCTION_HISTORY,
    )


class FileStatus(BaseModel):
    file_path_in_repo: Path
    contents: str


class ExpectedCommit(BaseModel):
    msg: str
    function_source_code: str


class CommitState(BaseModel):
    msg: str
    file_states: list[FileStatus]


class HistoryTestInfo(BaseModel):
    test_name: str
    commit_states: list[CommitState]
    expected: list[ExpectedCommit]


COMMIT_DETAILS = {
    ADD_NEW_DECORATOR: HistoryTestInfo(
        test_name=ADD_NEW_DECORATOR,
        commit_states=[
            CommitState(
                msg="add new decorator",
                file_states=[
                    FileStatus(
                        file_path_in_repo=Path("file1.py"),
                        contents=dedent(
                            f"""\
                            @traceability('{ADD_NEW_DECORATOR}')
                            def foo():
                                pass
                            """
                        ),
                    ),
                ],
            ),
        ],
        expected=[
            ExpectedCommit(
                msg="add new decorator",
                function_source_code="def foo():\n    pass",
            )
        ],
    ),
    DECORATOR_FUNCTION_RENAMED: HistoryTestInfo(
        test_name=DECORATOR_FUNCTION_RENAMED,
        commit_states=[
            CommitState(
                msg="add new decorator",
                file_states=[
                    FileStatus(
                        file_path_in_repo=Path("file2.py"),
                        contents=dedent(
                            f"""\
                            @traceability('{DECORATOR_FUNCTION_RENAMED}')
                            def foo():
                                pass
                            """
                        ),
                    ),
                ],
            ),
            CommitState(
                msg="rename decorated function",
                file_states=[
                    FileStatus(
                        file_path_in_repo=Path("file2.py"),
                        contents=dedent(
                            f"""\
                            @traceability('{DECORATOR_FUNCTION_RENAMED}')
                            def bar():
                                pass
                            """
                        ),
                    ),
                ],
            ),
        ],
        expected=[
            ExpectedCommit(
                msg="rename decorated function",
                function_source_code="def bar():\n    pass",
            ),
            ExpectedCommit(
                msg="add new decorator",
                function_source_code="def foo():\n    pass",
            ),
        ],
    ),
    DECORATOR_MOVED_TO_ANOTHER_FILE: HistoryTestInfo(
        test_name=DECORATOR_MOVED_TO_ANOTHER_FILE,
        commit_states=[
            CommitState(
                msg="add new decorator",
                file_states=[
                    FileStatus(
                        file_path_in_repo=Path("file3.py"),
                        contents=dedent(
                            f"""\
                            @traceability('{DECORATOR_MOVED_TO_ANOTHER_FILE}')
                            def foo():
                                pass
                            """
                        ),
                    ),
                ],
            ),
            CommitState(
                msg="move decorator to different function in new file",
                file_states=[
                    FileStatus(
                        file_path_in_repo=Path("file3.py"),
                        contents=dedent(
                            """\
                            def foo():
                                pass
                            """
                        ),
                    ),
                    FileStatus(
                        file_path_in_repo=Path("file4.py"),
                        contents=dedent(
                            f"""\
                            @traceability('{DECORATOR_MOVED_TO_ANOTHER_FILE}')
                            def bar():
                                pass
                            """
                        ),
                    ),
                ],
            ),
        ],
        expected=[
            ExpectedCommit(
                msg="move decorator to different function in new file",
                function_source_code="def bar():\n    pass",
            ),
            ExpectedCommit(
                msg="add new decorator",
                function_source_code="def foo():\n    pass",
            ),
        ],
    ),
}


def run_history_test(
    git_repo: Repo,
    tmp_path: Path,
    config: PyTraceabilityConfig,
    history_test_info: list[HistoryTestInfo] | HistoryTestInfo,
):
    if isinstance(history_test_info, HistoryTestInfo):
        history_test_info = [history_test_info]

    for test_info in history_test_info:
        for commit_state in test_info.commit_states:
            for file_status in commit_state.file_states:
                source_file = tmp_path / file_status.file_path_in_repo
                source_file.write_text(file_status.contents)
                git_repo.index.add(source_file)
            git_repo.index.commit(commit_state.msg)

    reports = list(PyTraceabilityCollector(config).collect())
    assert len(reports) == len(history_test_info)

    expected_history = {
        test_info.test_name: [
            M(
                TraceabilityGitHistory,
                message=e.msg,
                source_code=e.function_source_code,
            )
            for e in test_info.expected
        ]
        for test_info in history_test_info
    }
    actual_history = {a.key: a.history for a in reports}

    for key, expected in expected_history.items():
        assert key in actual_history
        actual_history_for_key = actual_history[key]
        assert actual_history_for_key is not None
        assert len(actual_history_for_key) == len(expected)
        for exp, act in zip(expected, actual_history_for_key):
            assert exp == act


@pytest.mark.parametrize("test_key", list(COMMIT_DETAILS.keys()))
def test_history(
    git_repo: Repo,
    tmp_path: Path,
    config: PyTraceabilityConfig,
    test_key: str,
):
    run_history_test(git_repo, tmp_path, config, COMMIT_DETAILS[test_key])


def test_run_all_history_tests(
    git_repo: Repo, tmp_path: Path, config: PyTraceabilityConfig
):
    run_history_test(git_repo, tmp_path, config, list(COMMIT_DETAILS.values()))


def test_independent_file_paths():
    """
    Test to ensure that file paths in COMMIT_DETAILS are unique across all test cases.
    The same file can be referenced multiple times within a single test case
    but must not overlap between different test cases.

    This is so that we can then run all of the independent test cases one after the other
    in a separate test case to test independence of the history processing code
    """
    test_case_to_file_paths = {
        key: {
            file_status.file_path_in_repo
            for commit_state in test_info.commit_states
            for file_status in commit_state.file_states
        }
        for key, test_info in COMMIT_DETAILS.items()
    }

    file_path_to_test_cases = {}
    for test_case, file_paths in test_case_to_file_paths.items():
        for file_path in file_paths:
            if file_path not in file_path_to_test_cases:
                file_path_to_test_cases[file_path] = []
            file_path_to_test_cases[file_path].append(test_case)

    for file_path, test_cases in file_path_to_test_cases.items():
        if len(test_cases) > 1:
            conflicting_test_cases = ", ".join(tc.value for tc in test_cases)
            raise AssertionError(
                f"File path conflict detected: {file_path}\n"
                f"Clashing test cases: {conflicting_test_cases}"
            )
