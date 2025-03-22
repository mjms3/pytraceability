from pytraceability.common import traceability


class pytraceability(traceability):
    def __init__(self, key: str, /, info: str):
        super().__init__(key, info=info)
