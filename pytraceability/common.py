from enum import Enum

from textwrap import dedent
from typing import Any, Mapping

from typing_extensions import Self

from pytraceability.data_definition import PyTraceabilityMode, Traceability

MetaDataType = Mapping[str, Any]

UNKNOWN = "UNKNOWN"


class TraceabilityErrorMessages(Enum):
    KEY_MUST_BE_ARG = "Expected the key to be provided as an arg"
    ONLY_ONE_ARG = "Traceability decorator must have only one arg"
    STATIC_MODE = f"In {PyTraceabilityMode.static_only} mode, all data must be static."
    KEY_CAN_NOT_BE_UNKNOWN = (
        "pytraceability must be able to work out a key for every decorator."
    )

    @classmethod
    def allowed_values(cls) -> tuple[str, ...]:
        return tuple(k.value for k in cls)


additional_error_info = {
    TraceabilityErrorMessages.KEY_MUST_BE_ARG: dedent("""\
    They key for the traceability decorator must be provided as an arg.
    This error should have been caught by type checks / run time errors before we ever
    get to here, but it is conceivable a custom decorator could bypass this expectation.
    """),
    TraceabilityErrorMessages.ONLY_ONE_ARG: dedent("""\
    The traceability decorator must have only one arg (the key).
    If you're using a custom traceability decorator, the __init__ should have signature:
    def __init__(self, key, *, arg1: str, arg2: str, ...):
    """),
    TraceabilityErrorMessages.STATIC_MODE: dedent(f"""\
    In f{PyTraceabilityMode.static_only} mode, all data must be defined in constants so that they
    can be extracted from the traceability decorator purely based on the source code. {PyTraceabilityMode.static_plus_dynamic}
    allows data in the decorators to be extracted dynamically, but this involves importing the code. WARNING: If your
    code has side effects that are not covered by a 'if __name__="__main__":' guard, these will be executed as part
    of the import.
    """),
    TraceabilityErrorMessages.KEY_CAN_NOT_BE_UNKNOWN: dedent(f"""\
    pytraceability needs to be able to determine a key for each traceability decorator. In {PyTraceabilityMode.static_only}
    this means the key must be a string. In {PyTraceabilityMode.static_plus_dynamic}, it could be a variable or determined
    on the fly but, there are some situations where this isn't done even at import time, for example in a closure where
    the key would only be determinable at run time.
    """),
}

assert set(additional_error_info.keys()) == set(
    TraceabilityErrorMessages
)  # Would be nice to do this by type checking


class InvalidTraceabilityError(Exception):
    allowed_message_starts = TraceabilityErrorMessages.allowed_values()

    def __init__(self, *args: str):
        if args and args[0] and not args[0].startswith(self.allowed_message_starts):
            raise ValueError(
                f"{args[0]} is not a valid {TraceabilityErrorMessages.__class__.__name__}"
            )
        super().__init__(*args)

    @classmethod
    def from_allowed_message_types(
        cls, msg_type: TraceabilityErrorMessages, additional_info: str = ""
    ) -> Self:
        return cls(msg_type.value + f" {additional_info}" if additional_info else "")


class traceability:
    def __init__(self, key: str, /, **kwargs) -> None:
        self.key = key
        self.metadata = kwargs

    def __call__(self, fn):
        if not hasattr(fn, "__traceability__"):
            fn.__traceability__ = []
        if self.key in {t.key for t in fn.__traceability__}:
            raise ValueError(
                f"{self.key} appears more than once on decorators for {fn.__name__}"
            )
        fn.__traceability__.append(Traceability(key=self.key, metadata=self.metadata))
        return fn
