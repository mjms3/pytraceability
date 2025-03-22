from pytraceability.common import traceability


class Foo:
    key = "A key"

    @traceability(key)
    def bar(self):
        pass
