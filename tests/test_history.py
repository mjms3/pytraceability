from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from textwrap import dedent
from unittest import mock

import pytest
from git import Repo

from pytraceability.config import GitHistoryMode, PyTraceabilityConfig
from pytraceability.data_definition import TraceabilityGitHistory
from pytraceability.discovery import collect_traceability_from_directory

GIT_HISTORY_TESTS_DIR = Path(__file__).parent / "git_history_tests"


class TestKey(Enum):
    ADD_NEW_DECORATOR = "add new decorator"
    DECORATOR_FUNCTION_RENAMED = "decorator function renamed"
    DECORATOR_MOVED_TO_ANOTHER_FILE = "decorator moved to another file"


@pytest.fixture()
def git_repo(tmp_path: Path) -> Repo:
    return Repo.init(tmp_path)


@pytest.fixture()
def config(tmp_path: Path) -> PyTraceabilityConfig:
    return PyTraceabilityConfig(
        repo_root=tmp_path,
        git_history_mode=GitHistoryMode.FUNCTION_HISTORY,
    )


@dataclass
class FileStatus:
    file_path_in_repo: Path
    contents: str


@dataclass
class ExpectedCommit:
    commit_number: int
    function_source_code: str


@dataclass
class CommitState:
    commit_number: int
    file_states: list[FileStatus]


@dataclass
class HistoryTestInfo:
    commit_states: list[CommitState]
    expected: list[ExpectedCommit]


COMMIT_DETAILS = {
    TestKey.ADD_NEW_DECORATOR: HistoryTestInfo(
        commit_states=[
            CommitState(
                commit_number=0,
                file_states=[
                    FileStatus(
                        Path("file1.py"),
                        dedent(
                            f"""\
                            @traceability('{TestKey.ADD_NEW_DECORATOR}')
                            def foo():
                                pass
                            """
                        ),
                    ),
                ],
            ),
        ],
        expected=[ExpectedCommit(0, "def foo():\n    pass")],
    ),
    TestKey.DECORATOR_FUNCTION_RENAMED: HistoryTestInfo(
        commit_states=[
            CommitState(
                commit_number=0,
                file_states=[
                    FileStatus(
                        Path("file2.py"),
                        dedent(
                            f"""\
                            @traceability('{TestKey.DECORATOR_FUNCTION_RENAMED}')
                            def foo():
                                pass
                            """
                        ),
                    ),
                ],
            ),
            CommitState(
                commit_number=1,
                file_states=[
                    FileStatus(
                        Path("file2.py"),
                        dedent(
                            f"""\
                            @traceability('{TestKey.DECORATOR_FUNCTION_RENAMED}')
                            def bar():
                                pass
                            """
                        ),
                    ),
                ],
            ),
        ],
        expected=[
            ExpectedCommit(1, "def bar():\n    pass"),
            ExpectedCommit(0, "def foo():\n    pass"),
        ],
    ),
    TestKey.DECORATOR_MOVED_TO_ANOTHER_FILE: HistoryTestInfo(
        commit_states=[
            CommitState(
                commit_number=0,
                file_states=[
                    FileStatus(
                        Path("file3.py"),
                        dedent(
                            f"""\
                            @traceability('{TestKey.DECORATOR_MOVED_TO_ANOTHER_FILE}')
                            def foo():
                                pass
                            """
                        ),
                    ),
                ],
            ),
            CommitState(
                commit_number=1,
                file_states=[
                    FileStatus(
                        Path("file3.py"),
                        dedent(
                            """\
                            def foo():
                                pass
                            """
                        ),
                    ),
                    FileStatus(
                        Path("file4.py"),
                        dedent(
                            f"""\
                            @traceability('{TestKey.DECORATOR_MOVED_TO_ANOTHER_FILE}')
                            def bar():
                                pass
                            """
                        ),
                    ),
                ],
            ),
        ],
        expected=[
            ExpectedCommit(1, "def bar():\n    pass"),
            ExpectedCommit(0, "def foo():\n    pass"),
        ],
    ),
}


def run_history_test(
    git_repo: Repo, tmp_path: Path, config: PyTraceabilityConfig, test_key: TestKey
):
    test_info = COMMIT_DETAILS[test_key]

    for commit_state in test_info.commit_states:
        for file_status in commit_state.file_states:
            source_file = tmp_path / file_status.file_path_in_repo
            source_file.write_text(file_status.contents)
            git_repo.index.add(source_file)
        git_repo.index.commit(f"Commit {commit_state.commit_number}")

    reports = list(collect_traceability_from_directory(tmp_path, tmp_path, config))
    assert len(reports) == 1
    actual = reports[0]

    expected_history = [
        TraceabilityGitHistory(
            commit=mock.ANY,
            author_name=mock.ANY,
            author_date=mock.ANY,
            message=f"Commit {expected_commit.commit_number}",
            source_code=expected_commit.function_source_code,
        )
        for expected_commit in test_info.expected
    ]
    assert actual.history == expected_history


@pytest.mark.parametrize("test_key", list(COMMIT_DETAILS.keys()))
def test_history(
    git_repo: Repo, tmp_path: Path, config: PyTraceabilityConfig, test_key: TestKey
):
    run_history_test(git_repo, tmp_path, config, test_key)


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
