from pytraceability.common import traceability


def bar():
    METADATA = "METADATA"

    @traceability(
        "A key",
        a=METADATA,
    )
    def foo():
        pass
