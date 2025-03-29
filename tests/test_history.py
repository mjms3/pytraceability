from pathlib import Path
from textwrap import dedent
from unittest import mock

import pytest
from git import Repo

from pytraceability.config import GitHistoryMode, PyTraceabilityConfig
from pytraceability.data_definition import TraceabilityGitHistory
from pytraceability.discovery import collect_traceability_from_directory

GIT_HISTORY_TESTS_DIR = Path(__file__).parent / "git_history_tests"


@pytest.fixture()
def git_repo(tmp_path: Path) -> Repo:
    return Repo.init(tmp_path)


@pytest.fixture()
def config(tmp_path: Path) -> PyTraceabilityConfig:
    return PyTraceabilityConfig(
        repo_root=tmp_path,
        git_history_mode=GitHistoryMode.FUNCTION_HISTORY,
    )


def test_decorator_added_at_same_time_as_function(
    git_repo: Repo, tmp_path: Path, config: PyTraceabilityConfig
):
    source_file = tmp_path / "file1.py"
    source_file.write_text(
        dedent("""\
    @traceability('KEY')
    def foo():
        pass
    """)
    )
    git_repo.index.add(source_file)
    commit_msg = "msg1"
    git_repo.index.commit(commit_msg)
    reports = list(collect_traceability_from_directory(tmp_path, tmp_path, config))
    assert len(reports) == 1
    actual = reports[0]

    assert actual.history == [
        TraceabilityGitHistory(
            commit=mock.ANY,
            author_name=mock.ANY,
            author_date=mock.ANY,
            message=commit_msg,
            source_code="def foo():\n    pass",
        )
    ]


def test_decorator_function_renamed(
    git_repo: Repo, tmp_path: Path, config: PyTraceabilityConfig
):
    source_file = tmp_path / "file2.py"
    source_file.write_text(
        dedent("""\
    @traceability('KEY')
    def foo():
        pass
    """)
    )
    git_repo.index.add(source_file)
    commit_msg1 = "msg1"
    git_repo.index.commit(commit_msg1)

    source_file = tmp_path / "file2.py"
    source_file.write_text(
        dedent("""\
        @traceability('KEY')
        def bar():
            pass
        """)
    )
    git_repo.index.add(source_file)
    commit_msg2 = "msg2"
    git_repo.index.commit(commit_msg2)

    reports = list(collect_traceability_from_directory(tmp_path, tmp_path, config))
    assert len(reports) == 1
    actual = reports[0]

    assert actual.history == [
        TraceabilityGitHistory(
            commit=mock.ANY,
            author_name=mock.ANY,
            author_date=mock.ANY,
            message=commit_msg2,
            source_code="def bar():\n    pass",
        ),
        TraceabilityGitHistory(
            commit=mock.ANY,
            author_name=mock.ANY,
            author_date=mock.ANY,
            message=commit_msg1,
            source_code="def foo():\n    pass",
        ),
    ]
