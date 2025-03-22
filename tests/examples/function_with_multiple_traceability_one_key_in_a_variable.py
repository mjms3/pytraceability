from pytraceability.common import traceability

ANOTHER_KEY = "Another key"


@traceability(ANOTHER_KEY)
@traceability("A key")
def foo():
    pass
