from pytraceability.common import traceability

VALUE_STORED_IN_VARIABLE = "Variable value"


@traceability("A key", a=VALUE_STORED_IN_VARIABLE)
def foo():
    pass
