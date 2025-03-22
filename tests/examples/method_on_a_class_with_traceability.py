from pytraceability.common import traceability


class Foo:
    @traceability("A key")
    def bar(self):
        pass
