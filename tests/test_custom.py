import pytest

from pytraceability.custom import pytraceability


@pytest.mark.raises(exception=TypeError)
def test_custom_decorator_requires_info():
    @pytraceability("PYTRACEABILITY-1")  # pyright: ignore
    def foo():
        pass


@pytest.mark.raises(exception=ValueError)
def test_custom_decorator_key_must_start_with_PYTRACEABILITY():
    @pytraceability("PYTRCAEABILITY-1", info="info")
    def foo():
        pass


@pytest.mark.raises(exception=TypeError)
def test_custom_decorator_info_must_be_a_keyword_argument():
    @pytraceability("PYTRACEABILITY-1", "info")  # pyright: ignore
    def foo():
        pass
