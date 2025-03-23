from pytraceability.common import traceability


@traceability("A key")
def foo():
    print("blah")
    pass
