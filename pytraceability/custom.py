from pytraceability.common import traceability
from pytraceability.config import PROJECT_NAME


class pytraceability(traceability):
    def __init__(self, key: str, *, info: str):
        REQUIRED_PREFIX = f"{PROJECT_NAME.upper()}-"
        if not key.startswith(REQUIRED_PREFIX):
            raise ValueError(f"Key {key} does not start with {REQUIRED_PREFIX}")
        super().__init__(key, info=info)
