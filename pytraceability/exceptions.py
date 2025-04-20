from __future__ import annotations

from enum import Enum
from textwrap import dedent
from typing_extensions import Self

from pytraceability.config import PROJECT_NAME


class TraceabilityErrorMessages(Enum):
    KEY_MUST_BE_ARG = "Expected the key to be provided as an arg"
    ONLY_ONE_ARG = "Traceability decorator must have only one arg"
    KEY_CAN_NOT_BE_DYNAMIC = (
        f"{PROJECT_NAME} must be able to work out a key for every decorator."
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
    TraceabilityErrorMessages.KEY_CAN_NOT_BE_DYNAMIC: dedent(f"""\
    {PROJECT_NAME} requires the key to be dynamic. This is required for the repository mining to extract traceability data
    to work.
    """),
}


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
