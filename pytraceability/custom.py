from pytraceability.common import traceability


class pytraceability(traceability):
    def __init__(self, key: str, /, info: str):
        REQUIRED_PREFIX = "PYTRACEABILITY-"
        if not key.startswith(REQUIRED_PREFIX):
            raise ValueError(f"Key {key} does not start with {REQUIRED_PREFIX}")
        super().__init__(key, info=info)
