from pytraceability.common import traceability


def foo():
    @traceability("A key")
    def bar():
        pass
