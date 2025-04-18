from pytraceability.common import traceability


def foo():
    METADATA = "METADATA-STRING"

    @traceability(
        "A key",
        a=METADATA,
    )
    def bar():
        pass
