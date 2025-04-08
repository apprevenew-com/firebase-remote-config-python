from datetime import datetime
from typing import Optional

import pyparsing as pp
import pytz

from . import conditions as cond
from . import enums
from . import validation as valid

# helper functions

def in_parentheses(el: pp.ParserElement) -> pp.ParserElement:
    """Returns a ParseElement with parentheses around the provided element."""
    return "(" + el + ")"


def in_brackets(el: pp.ParserElement) -> pp.ParserElement:
    """Returns a ParseElement with brackets around the provided element."""
    return "[" + el + "]"


# literals

literal_str = pp.QuotedString("'")
literal_int = pp.common.signed_integer()
literal_uint = pp.common.integer()


def set_tz(toks: pp.ParseResults):
    """Parse action that applies provided timezone (tz token) to datetime (dt token)."""
    dt: datetime = toks.dt
    if toks.tz:
        dt = dt.replace(tzinfo=pytz.timezone(toks.tz))
    return dt


literal_dt = literal_str.copy().add_parse_action(pp.common.convert_to_datetime(fmt=cond.DATETIME_FORMAT))("dt")
literal_dt = literal_dt + pp.Opt("," + literal_str("tz"))
literal_dt.set_parse_action(set_tz)


# percent conditions

percent = pp.Keyword("percent", caseless=True) + pp.Opt(in_parentheses(literal_str("seed")))
percent_ops = pp.one_of([enums.PercentConditionOperator.GREATER_THAN.value, enums.PercentConditionOperator.LESS_OR_EQUAL.value])

percent_condition_binary = percent + percent_ops("op") + literal_uint("percent")
percent_condition_binary = percent_condition_binary.set_parse_action(lambda toks: cond.PercentCondition(
    percent=toks.percent,
    percentOperator=enums.PercentConditionOperator(toks.op),
    seed=toks.seed,
))

percent_condition_ternary = percent + pp.Keyword("between", caseless=True) + literal_uint("lower_bound") + pp.Keyword("and", caseless=True) + literal_uint("upper_bound")
percent_condition_ternary = percent_condition_ternary.set_parse_action(lambda toks: cond.PercentCondition(
    percentRange=cond.PercentRange(
        lowerBound=toks.lower_bound,
        upperBound=toks.upper_bound,
    ),
    percentOperator=enums.PercentConditionOperator.BETWEEN,
    seed=toks.seed,
))

percent_condition = percent_condition_binary | percent_condition_ternary

# element conditions

value_single_str = literal_str("value_single")
value_single_int = literal_int("value_single")
value_single_timestamp = in_parentheses(literal_dt("value_single"))
value_single_datetime = pp.Keyword("datetime", caseless=True) + in_parentheses(literal_dt("value_single"))
value_array_str = in_brackets(pp.DelimitedList(literal_str)("value_array"))


def value(name: enums.ElementName, op: enums.ElementOperator) -> pp.ParserElement:
    """Returns ParserElement for a value depending on provided element name and operator."""
    if valid.needs_single_value(op):
        if valid.supports_value_str(name, op):
            expr = in_brackets(value_single_str) | value_single_str | value_single_datetime | value_single_timestamp
        if valid.supports_value_number(name, op):
            expr = value_single_int
    else:
        expr = value_array_str

    if valid.needs_parentheses(op):
        expr = in_parentheses(expr)
    return expr


def supported(el_name: enums.ElementName, op: enums.ElementOperator) -> bool:
    """Checks if provided pair of element name and operator is supported."""
    return valid.supports_name_operator(el_name, op)


def make_element_condition(el_name: enums.ElementName, op: enums.ElementOperator) -> Optional[pp.ParserElement]:
    """Returns ParserElement for element condition for the provided element name and operator."""
    expr = pp.Keyword(el_name.value)("element")

    if valid.supports_key(el_name):
        expr = expr + in_brackets(literal_str("key"))

    if valid.needs_dot(op):
        expr = expr + "."
    expr = expr + pp.Keyword(op.value)("op")

    expr = expr + value(el_name, op)

    expr.set_parse_action(lambda toks: cond.ElementCondition(
        element=cond.Element(
            name=el_name,
            key=toks.key or None,
        ),
        operator=op,
        values=list(toks.value_array) or None,
        value=toks.value_single or None,
    ))

    return expr


element_operators = list(enums.ElementOperatorMethodString) + list(enums.ElementOperatorMethodSemantic) + list(enums.ElementOperatorBinary) + list(enums.ElementOperatorBinaryArray) + list(enums.ElementOperatorAudiences)
element_conditions = [make_element_condition(el_name, op) for el_name in enums.ElementName for op in element_operators if supported(el_name, op)]
element_condition = pp.MatchFirst(element_conditions)


# other conditions

true_condition = pp.Keyword("true", caseless=True).set_parse_action(lambda _: cond.TrueCondition())
false_condition = pp.Keyword("false", caseless=True).set_parse_action(lambda _: cond.FalseCondition())


# pattern

condition = true_condition | false_condition | percent_condition | element_condition
logical_and = pp.Keyword("&&")
pattern = pp.DelimitedList(condition, logical_and)("conditions")
pattern = pattern.set_parse_action(lambda toks: cond.AndCondition(conditions=list(toks.conditions)))


# api

class ConditionParser():
    """Class to parse conditions."""
    def __init__(self):
        self.pattern = pattern

    def parse(self, input: str) -> cond.AndCondition:
        """Parses the input string and returns the parsed condition."""
        res = pattern.parse_string(input, parse_all=True)
        return res[0]
