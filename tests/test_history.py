from dataclasses import replace
from unittest import mock

from pytraceability.config import GitHistoryMode
from tests.examples import function_with_traceability
from tests.factories import _test_from_module, TEST_CONFIG


def test_line_based_git_history():
    config = replace(TEST_CONFIG, git_history_mode=GitHistoryMode.FUNCTION_HISTORY)
    _test_from_module(
        function_with_traceability, config=config, history=[mock.ANY, mock.ANY]
    )
