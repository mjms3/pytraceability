from pytraceability.common import traceability


@traceability("A key", a="b")
def foo():
    pass
