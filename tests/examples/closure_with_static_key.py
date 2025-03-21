from pytraceability.common import traceability


def bar():
    @traceability("A key")
    def foo():
        pass
