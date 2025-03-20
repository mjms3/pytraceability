from pytraceability.discovery import traceability


def bar():
    @traceability("A key")
    def foo():
        pass
