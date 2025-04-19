import pytest

from pytraceability.custom import pytraceability


def test_custom_decorator_requires_info():
    with pytest.raises(TypeError):

        @pytraceability("PYTRACEABILITY-1")  # pyright: ignore
        def foo():
            pass


def test_custom_decorator_key_must_start_with_PYTRACEABILITY():
    with pytest.raises(ValueError):

        @pytraceability("PYTRCAEABILITY-1", info="info")
        def foo():
            pass


def test_custom_decorator_info_must_be_a_keyword_argument():
    with pytest.raises(TypeError):

        @pytraceability("PYTRACEABILITY-1", "info")  # pyright: ignore
        def foo():
            pass
