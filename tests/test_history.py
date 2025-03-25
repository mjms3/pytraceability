from dataclasses import replace
from pathlib import Path
from unittest import mock

import pytest

from pytraceability.config import GitHistoryMode
from pytraceability.data_definition import TraceabilityGitHistory
from pytraceability.discovery import collect_traceability_from_directory
from tests.factories import TEST_CONFIG

GIT_HISTORY_TESTS_DIR = Path(__file__).parent / "git_history_tests"
SHOW_HISTORY_CONFIG = replace(
    TEST_CONFIG, git_history_mode=GitHistoryMode.FUNCTION_HISTORY
)


@pytest.fixture(scope="session")
def traceability_reports():
    return list(
        collect_traceability_from_directory(
            GIT_HISTORY_TESTS_DIR, GIT_HISTORY_TESTS_DIR, SHOW_HISTORY_CONFIG
        )
    )


def test_decorator_added_at_same_time_as_function(traceability_reports):
    key = "GIT-HISTORY-TEST-1"
    relevant_reports = [t for t in traceability_reports if t.key == key]
    assert len(relevant_reports) == 1
    actual = relevant_reports[0]

    assert actual.history == [
        TraceabilityGitHistory(
            commit=mock.ANY,
            author_name=mock.ANY,
            author_date=mock.ANY,
            message="History test setup: Add a file with a decorator",
            source_code="def first_function():\n    pass",
        )
    ]


def test_decorator_added_to_preexisting_function(traceability_reports):
    key = "GIT-HISTORY-TEST-2"
    relevant_reports = [t for t in traceability_reports if t.key == key]
    assert len(relevant_reports) == 1
    actual = relevant_reports[0]

    assert actual.history == [
        TraceabilityGitHistory(
            commit=mock.ANY,
            author_name=mock.ANY,
            author_date=mock.ANY,
            message="History test setup: Add a decorator to an existing function",
            source_code="def second_function():\n    pass",
        ),
    ]


def test_decorator_function_renamed(traceability_reports):
    key = "GIT-HISTORY-TEST-3"
    relevant_reports = [t for t in traceability_reports if t.key == key]
    assert len(relevant_reports) == 1
    actual = relevant_reports[0]

    assert actual.history == [
        TraceabilityGitHistory(
            commit=mock.ANY,
            author_name=mock.ANY,
            author_date=mock.ANY,
            message="History test setup: Rename an existing function",
            source_code="def new_function_name():\n    pass",
        ),
        TraceabilityGitHistory(
            commit=mock.ANY,
            author_name=mock.ANY,
            author_date=mock.ANY,
            message="History test setup: Add a function to be renamed",
            source_code="def original_function_name():\n    pass",
        ),
    ]
