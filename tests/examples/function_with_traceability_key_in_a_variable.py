from pytraceability.discovery import traceability

_KEY = "A key"


@traceability(key=_KEY)
def foo():
    pass
