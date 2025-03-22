import pytest

from pytraceability.custom import pytraceability


@pytest.mark.raises(exception=TypeError)
def test_custom_decorator_requires_info():
    @pytraceability("PYTRCAEABILITY-1")  # pyright: ignore
    def foo():
        pass


@pytest.mark.raises(exception=ValueError)
def test_custom_decorator_key_must_start_with_PYTRACEABILITY():
    @pytraceability("PYTRCAEABILITY-1", info="info")
    def foo():
        pass
