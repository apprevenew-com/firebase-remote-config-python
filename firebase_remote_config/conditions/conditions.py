from __future__ import annotations

from datetime import datetime
from typing import Annotated, List, Optional, Union

from pydantic import BaseModel, Field, model_validator

from . import enums
from . import validation as valid

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def str_custom_value(v: enums.CustomValue) -> str:
    """Converts CustomValue to a string."""
    if type(v) is str:
        return f"'{v}'"

    if type(v) is int:
        return str(v)

    if type(v) is float:
        return str(v)

    if isinstance(v, datetime):
        v_str = v.strftime(DATETIME_FORMAT)
        parts = [v_str]

        if v.tzinfo:
            tz_str = datetime.tzname(v)

            if tz_str == "GMT":
                tz_str = "Etc/GMT"  # Firebase Remote Config uses Etc/GMT for GMT

            parts = [v_str, tz_str]

        parts = [f"'{p}'" for p in parts]
        v_str = ", ".join(parts)
        return f"{v_str}"


# conditions

class Element(BaseModel):
    """An element with optional key. Only app.userProperty and app.customSignal elements support keys."""
    name: enums.ElementName
    key: Optional[str] = None

    def __repr__(self):
        if self.key:
            return f"{self.name.value}['{self.key}']"
        return self.name.value

    __str__ = __repr__

class ElementCondition(BaseModel):
    """
    Matches users based on the value(s) of an element, such as app version, user property, or custom signal.
    Example:
    app.userProperty['paywall_name'].contains(['test_paywall'])
    |______________| |____________|  |______| |______________|
    element.name     element.key     operator  values
    """

    element: Element  # Element with optional key.
    operator: enums.ElementOperator  # The choice of custom operator to determine how to compare targets to value(s).
    values: Optional[Annotated[List[enums.CustomValue], Field(min_length=1)]] = None  # A list of target custom values
    value: Optional[enums.CustomValue] = None  # A single target custom value

    @model_validator(mode="after")
    def validate(self):
        valid.validate_element_condition(self.element.name, self.element.key, self.operator, self.value, self.values)
        return self

    def __repr__(self):
        if isinstance(self.operator, enums.ElementOperatorBinary):
            v = self.value
            v = str_custom_value(v)

            if self.element.name == enums.ElementName.DEVICE_DATETIME:
                v = f"dateTime({v})"
            if self.element.name == enums.ElementName.APP_FIRST_OPEN_TIMESTAMP:
                v = f"({v})"

            return f"{self.element} {self.operator.value} {v}"

        if isinstance(self.operator, enums.ElementOperatorMethodSemantic):
            v = self.value
            v = str_custom_value(v)
            return f"{self.element}.{self.operator.value}([{v}])"

        if isinstance(self.operator, (enums.ElementOperatorMethodString, enums.ElementOperatorMethodAudiences)):
            xv = [str_custom_value(v) for v in self.values]
            xv = ", ".join(xv)
            xv = f"[{xv}]"
            return f"{self.element}.{self.operator.value}({xv})"

        if isinstance(self.operator, enums.ElementOperatorBinaryArray):
            xv = [str_custom_value(v) for v in self.values]
            xv = ", ".join(xv)
            xv = f"[{xv}]"
            return f"{self.element} {self.operator.value} {xv}"

        raise ValueError(f"Unexpected CustomOperator: {self.operator.value}")

    __str__ = __repr__


class PercentRange(BaseModel):
    """A range of percentiles."""

    lowerBound: Annotated[int, Field(ge=0, le=100)]  # The lower limit of percentiles to target in percents. The value must be in the range [0 and 100].
    upperBound: Annotated[int, Field(ge=0, le=100)]  # The upper limit of percentiles to target in percents. The value must be in the range [0 and 100].

    @model_validator(mode="after")
    def validate(self):
        """Validates the PercentRange."""
        if self.lowerBound > self.upperBound:
            raise ValueError("percentLowerBound must be less than or equal to percentUpperBound")
        return self


class PercentCondition(BaseModel):
    """Matches users based on whether the user falls into a certain percentile range."""

    percent: Optional[int] = None  # The limit of percentiles to target in percents when using the LESS_OR_EQUAL and GREATER_THAN operators. The value must be in the range [0 and 100].
    percentRange: Optional[PercentRange] = None  # The percent interval to be used with the BETWEEN operator.
    percentOperator: enums.PercentConditionOperator  # The choice of percent operator to determine how to compare targets to percent(s).
    seed: Optional[str] = None  # The seed used when evaluating the hash function to map an instance to a value in the hash space. This is a string which can have 0 - 32 characters and can contain ASCII characters [-_.0-9a-zA-Z].The string is case-sensitive.

    @model_validator(mode="after")
    def validate(self):
        """Validates the PercentCondition."""
        if self.percentOperator == enums.PercentConditionOperator.BETWEEN and not self.percentRange:
            raise ValueError("percentRange must be used with BETWEEN percentOperator")
        if self.percentOperator in [enums.PercentConditionOperator.GREATER_THAN, enums.PercentConditionOperator.LESS_OR_EQUAL] and not self.percent:
            raise ValueError(f"percent must be used with {self.percentOperator.value} percentOperator")
        return self

    def __repr__(self):
        if self.seed:
            seed = f"('{self.seed}')"
        else:
            seed = ""

        if self.percentOperator == enums.PercentConditionOperator.BETWEEN:
            return f"percent{seed} between {self.percentRange.lowerBound} and {self.percentRange.upperBound}"

        if self.percentOperator in [enums.PercentConditionOperator.GREATER_THAN, enums.PercentConditionOperator.LESS_OR_EQUAL]:
            return f"percent{seed} {self.percentOperator.value} {self.percent}"

        raise ValueError("Unexpected PercentConditionOperator")

    __str__ = __repr__


class FalseCondition(BaseModel):
    """Matches no users."""

    def __repr__(self):
        return "false"

    __str__ = __repr__


class TrueCondition(BaseModel):
    """Matches all users."""

    def __repr__(self):
        return "true"

    __str__ = __repr__


class AndCondition(BaseModel):
    """Matches users if all of the conditions are met."""

    conditions: List[AtomCondition]  # The list of conditions.

    def __repr__(self):
        return f"{' && '.join([repr(c) for c in self.conditions])}"

    __str__ = __repr__


AtomCondition = Union[ElementCondition, PercentCondition, FalseCondition, TrueCondition]

Condition = Union[AndCondition, ElementCondition, PercentCondition, FalseCondition, TrueCondition]


class NamedCondition(BaseModel):
    """A condition with a name."""
    name: str  # The name of the condition.
    condition: Condition  # The condition object.

    def __repr__(self):
        return repr(self.condition)

    __str__ = __repr__
