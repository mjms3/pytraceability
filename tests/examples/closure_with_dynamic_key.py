from pytraceability.discovery import traceability


def bar():
    KEY_VARIABLE = "A key"

    @traceability(KEY_VARIABLE)
    def foo():
        pass
