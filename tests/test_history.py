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
    traceability_reports = list(
        collect_traceability_from_directory(
            GIT_HISTORY_TESTS_DIR, GIT_HISTORY_TESTS_DIR, SHOW_HISTORY_CONFIG
        )
    )
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
            diff="@@ -0,0 +1,6 @@\n"
            "+from pytraceability.common import traceability\n"
            "+\n"
            "+\n"
            '+@traceability("GIT-HISTORY-TEST-1")\n'
            "+def first_function():\n"
            "+    pass\n",
        )
    ]


def test_decorator_added_to_preexisting_function():
    traceability_reports = list(
        collect_traceability_from_directory(
            GIT_HISTORY_TESTS_DIR, GIT_HISTORY_TESTS_DIR, SHOW_HISTORY_CONFIG
        )
    )
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
            diff="@@ -1,2 +1,6 @@\n"
            "+from pytraceability.common import traceability\n"
            "+\n"
            "+\n"
            '+@traceability("GIT-HISTORY-TEST-2")\n'
            " def second_function():\n"
            "     pass\n",
        ),
    ]


def test_decorator_function_renamed():
    traceability_reports = list(
        collect_traceability_from_directory(
            GIT_HISTORY_TESTS_DIR, GIT_HISTORY_TESTS_DIR, SHOW_HISTORY_CONFIG
        )
    )
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
            diff="@@ -2,5 +2,5 @@ from pytraceability.common "
            "import traceability\n"
            " \n"
            " \n"
            ' @traceability("GIT-HISTORY-TEST-3")\n'
            "-def original_function_name():\n"
            "+def new_function_name():\n"
            "     pass\n",
        ),
        TraceabilityGitHistory(
            commit=mock.ANY,
            author_name=mock.ANY,
            author_date=mock.ANY,
            message="History test setup: Add a function to be renamed",
            diff="@@ -0,0 +1,6 @@\n"
            "+from pytraceability.common import traceability\n"
            "+\n"
            "+\n"
            '+@traceability("GIT-HISTORY-TEST-3")\n'
            "+def original_function_name():\n"
            "+    pass\n",
        ),
    ]
