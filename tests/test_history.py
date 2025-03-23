from dataclasses import replace
from pathlib import Path
from unittest import mock

from pytraceability.config import GitHistoryMode
from pytraceability.data_definition import TraceabilityGitHistory
from pytraceability.discovery import collect_traceability_from_directory
from tests.factories import TEST_CONFIG

GIT_HISTORY_TESTS_DIR = Path(__file__).parent / "git_history_tests"
SHOW_HISTORY_CONFIG = replace(
    TEST_CONFIG, git_history_mode=GitHistoryMode.FUNCTION_HISTORY
)


def test_decorator_added_at_same_time_as_function():
    actual = list(
        collect_traceability_from_directory(
            GIT_HISTORY_TESTS_DIR, GIT_HISTORY_TESTS_DIR, SHOW_HISTORY_CONFIG
        )
    )
    assert len(actual) == 1
    assert actual[0].history == [
        TraceabilityGitHistory(
            commit=mock.ANY,
            author_name=mock.ANY,
            author_date=mock.ANY,
            message="History test setup: Add a file with a decorator",
            diff=mock.ANY,
        )
    ]
