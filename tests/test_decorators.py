import pytest

from pytraceability.common import traceability, Traceability


def test_decorated_function_executes():
    @traceability("KEY")
    def foo(x):
        return x + 1

    assert foo(1) == 2


def test_decorated_function_has_correct_name():
    @traceability("KEY")
    def foo(x):
        return x + 1

    assert foo.__name__ == "foo"


def test_traceability_decorators_stack():
    @traceability("KEY 2")
    @traceability("KEY 1")
    def foo(x):
        return x + 1

    assert getattr(foo, "__traceability__") == [
        Traceability("KEY 1"),
        Traceability("KEY 2"),
    ]


@pytest.mark.raises(exception=ValueError)
def test_the_same_key_cannot_be_used_twice_on_a_function():
    @traceability("KEY")
    @traceability("KEY")
    def foo(x):
        return x + 1
