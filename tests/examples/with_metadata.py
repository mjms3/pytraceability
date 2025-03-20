from pytraceability.discovery import traceability


@traceability("A key", a="b")
def foo():
    pass
