from pytraceability.common import traceability


def foo():
    METADATA = "METADATA"

    @traceability(
        "A key",
        a=METADATA,
    )
    def bar():
        pass
