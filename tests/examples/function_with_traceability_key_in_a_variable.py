from pytraceability.common import traceability

_KEY = "A key"


@traceability(_KEY)
def foo():
    pass
