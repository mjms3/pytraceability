from __future__ import annotations

from pydantic import BaseModel


class PydanticModelMatcher:
    def __init__(self, expected_type: type[BaseModel], **expected_fields):
        self.expected_type = expected_type
        self.expected_fields = expected_fields

    def __eq__(self, other):
        if not isinstance(other, self.expected_type):
            raise TypeError(
                f"Expected model of type {self.expected_type}, but got {type(other)}"
            )

        mismatches = {}
        for field, expected_value in self.expected_fields.items():
            if field not in other.model_fields:
                raise ValueError(
                    f"Field '{field}' is not part of the model {self.expected_type.__name__}"
                )

            actual_value = getattr(other, field, None)
            if actual_value != expected_value:
                mismatches[field] = (expected_value, actual_value)

        if mismatches:
            raise AssertionError(
                "Model fields did not match:\n"
                + "\n".join(
                    f"  {field}: expected {exp!r}, got {act!r}"
                    for field, (exp, act) in mismatches.items()
                )
            )
        return True

    def __repr__(self):
        return f"ModelMatcher({self.expected_type}, {self.expected_fields})"


M = PydanticModelMatcher
