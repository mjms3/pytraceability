from __future__ import annotations

from enum import Enum
from textwrap import dedent
from typing_extensions import Self


class TraceabilityErrorMessages(Enum):
    KEY_MUST_BE_UNIQUE = "Key must be unique"
    ONLY_ONE_ARG = "Traceability decorator must have only one arg"

    KEY_CAN_ONLY_BE_SPECIFIED_ONCE = (
        "Key can only be specified once in a single decorator."
    )
    KEY_MUST_BE_SPECIFIED = "Key must be specified"
    KEY_MUST_BE_A_STRING = "Key must be a string"

    @classmethod
    def allowed_values(cls) -> tuple[str, ...]:
        return tuple(k.value for k in cls)


additional_error_info = {
    TraceabilityErrorMessages.KEY_MUST_BE_UNIQUE: dedent("""\
    The key for the traceability decorator must be unique.
    This is to allow the repository mining to extract historic traceability data to work.
    """),
    TraceabilityErrorMessages.ONLY_ONE_ARG: dedent("""\
    The traceability decorator must have only one arg (the key).
    If you're using a custom traceability decorator, a possible signature for the
     __init__ could be signature:
    def __init__(self, key, *, arg1: str, arg2: str, ...):
    """),
    TraceabilityErrorMessages.KEY_CAN_ONLY_BE_SPECIFIED_ONCE: dedent("""\
    The key for the traceability decorator can only be specified once that is,
    either as an arg or as a kwarg."""),
    TraceabilityErrorMessages.KEY_MUST_BE_SPECIFIED: dedent("""\
    The key for the traceability decorator must be specified, either as an arg or as a kwarg
    named 'key'.
    """),
    TraceabilityErrorMessages.KEY_MUST_BE_A_STRING: dedent("""\
    The key for the traceability decorator must be a string (and set statically).
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
