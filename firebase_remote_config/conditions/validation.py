from datetime import datetime
from typing import Dict, List, Optional

from . import enums


def must_have_key(name: enums.ElementName) -> bool:
    """
    Check if an element name supports a key.
    :param ElementName name: The name of the element.
    """
    supported_names = [enums.ElementName.APP_USER_PROPERTY, enums.ElementName.APP_CUSTOM_SIGNAL]
    return name in supported_names

def supports_name_operator(name: enums.ElementName, op: enums.ElementOperator) -> bool:
    """
    Check if an element supports an operator.
    :param ElementName name: The name of the element.
    :param ElementOperator op: The operator to check.
    """
    supported_ops = get_supported_ops(name)
    return supported_ops and op in supported_ops

def get_supported_ops(name: enums.ElementName) -> List[enums.ElementOperator]:
    """
    Get the list of operators that can be used with a specific element name.
    Different elements support different operators based on their data type and Firebase Remote Config capabilities.
    :param ElementName name: The name of the element.
    Raises:
    ValueError: If an unsupported ElementName is provided.
    """

    supported_ops_dict: Dict[enums.ElementName, List[enums.ElementOperator]] = {
        enums.ElementName.APP_BUILD: list(enums.ElementOperatorMethodSemantic) + list(enums.ElementOperatorMethodString),
        enums.ElementName.APP_VERSION: list(enums.ElementOperatorMethodSemantic) + list(enums.ElementOperatorMethodString),
        enums.ElementName.APP_ID: [enums.ElementOperatorBinary.EQ],
        enums.ElementName.APP_AUDIENCES: list(enums.ElementOperatorMethodAudiences),
        enums.ElementName.APP_IMPORTED_SEGMENTS: list(enums.ElementOperatorMethodAudiences),
        enums.ElementName.APP_FIRST_OPEN_TIMESTAMP: [enums.ElementOperatorBinary.LTE, enums.ElementOperatorBinary.GT],
        enums.ElementName.DEVICE_DATETIME: [enums.ElementOperatorBinary.LT, enums.ElementOperatorBinary.GTE],
        enums.ElementName.APP_FIREBASE_INSTALLATION_ID: list(enums.ElementOperatorBinaryArray),
        enums.ElementName.APP_USER_PROPERTY: list(enums.ElementOperatorBinary) + list(enums.ElementOperatorMethodString),
        enums.ElementName.APP_CUSTOM_SIGNAL: list(enums.ElementOperatorBinary) + list(enums.ElementOperatorMethodString),
        enums.ElementName.DEVICE_COUNTRY: list(enums.ElementOperatorBinaryArray),
        enums.ElementName.DEVICE_LANGUAGE: list(enums.ElementOperatorBinaryArray),
        enums.ElementName.DEVICE_OS: [enums.ElementOperatorBinary.EQ, enums.ElementOperatorBinary.NEQ],
    }

    supported = supported_ops_dict.get(name)
    if supported:
        return supported
    raise ValueError(f"Unexpected ElementName: {name.name}")


def needs_single_value(op: enums.ElementOperator) -> bool:
    """
    Checks if an operator needs a single value only.
    :param ElementOperator op: The operator to check.
    Raises:
        ValueError: If an unknown operator is provided.
    """
    if isinstance(op, (enums.ElementOperatorBinary, enums.ElementOperatorMethodSemantic)):
        return True
    if isinstance(op, (enums.ElementOperatorMethodString, enums.ElementOperatorBinaryArray, enums.ElementOperatorMethodAudiences)):
        return False
    raise ValueError(f"Unknown operator: {op}")


def has_method_syntax(op: enums.ElementOperator) -> bool:
    """
    Checks if an operator has method syntax, i.e. element_name.<operator>([value1, ...])
    :param ElementOperator op: The operator to check.
    Raises:
        ValueError: If an unknown operator is provided.
    """
    if isinstance(op, (enums.ElementOperatorMethodString, enums.ElementOperatorMethodSemantic, enums.ElementOperatorMethodAudiences)):
        return True
    if isinstance(op, (enums.ElementOperatorBinary, enums.ElementOperatorBinaryArray)):
        return False
    raise ValueError(f"Unknown operator: {op}")

def supports_datetime(name: enums.ElementName) -> bool:
    """
    Checks if element name supports datetime values.
    :param ElementName name: The name of the element.
    """
    return name == enums.ElementName.DEVICE_DATETIME

def supports_timestamp(name: enums.ElementName) -> bool:
    """
    Checks if element name supports timestamp values.
    :param ElementName name: The name of the element.
    """
    return name == enums.ElementName.APP_FIRST_OPEN_TIMESTAMP


def is_str(v: enums.CustomValue):
    """Checks if CustomValue is a string."""
    return type(v) is str


def is_number(v: enums.CustomValue):
    """Checks if CustomValue is a number."""
    return type(v) is int or type(v) is float


def validate_element_condition(name: enums.ElementName, key: Optional[str], op: enums.ElementOperator, value: Optional[enums.CustomValue], values: Optional[List[enums.CustomValue]]):
    if key and not must_have_key(name):
        raise ValueError(f"{name.value} name does not support key")

    if not key and must_have_key(name):
        raise ValueError(f"{name.value} name requires a key")

    # single value
    if value is not None:
        if is_str(value):
            if name == enums.ElementName.APP_BUILD:
                allowed_ops = list(enums.ElementOperatorMethodSemantic)
            elif name == enums.ElementName.APP_VERSION:
                allowed_ops = list(enums.ElementOperatorMethodSemantic)
            elif name == enums.ElementName.APP_ID:
                allowed_ops = [enums.ElementOperatorBinary.EQ]
            elif name == enums.ElementName.DEVICE_OS:
                allowed_ops = [enums.ElementOperatorBinary.EQ, enums.ElementOperatorBinary.NEQ]

            elif name == enums.ElementName.APP_AUDIENCES:
                allowed_ops = list(enums.ElementOperatorMethodAudiences)
                raise ValueError(f"Single str value is not supported by {name.value} and {op.value}. Must be passed as array and operator must be one of: {', '.join([o.value for o in allowed_ops])}")
            elif name == enums.ElementName.APP_IMPORTED_SEGMENTS:
                allowed_ops = list(enums.ElementOperatorMethodAudiences)
                raise ValueError(f"Single str value is not supported by {name.value} and {op.value}. Must be passed as array and operator must be one of: {', '.join([o.value for o in allowed_ops])}")
            elif name in [enums.ElementName.APP_USER_PROPERTY, enums.ElementName.APP_CUSTOM_SIGNAL]:
                allowed_ops = list(enums.ElementOperatorMethodString)
                raise ValueError(f"Single str value is not supported by {name.value} and {op.value}. Must be passed as array and operator must be one of: {', '.join([o.value for o in allowed_ops])}")
            elif name in [enums.ElementName.APP_FIREBASE_INSTALLATION_ID, enums.ElementName.DEVICE_COUNTRY, enums.ElementName.DEVICE_LANGUAGE]:
                allowed_ops = list(enums.ElementOperatorBinaryArray)
                raise ValueError(f"Single str value is not supported by {name.value} and {op.value}. Must be passed as array and operator must be one of: {', '.join([o.value for o in allowed_ops])}")

            else:
                allowed_names = [
                    enums.ElementName.APP_BUILD,
                    enums.ElementName.APP_VERSION,
                    enums.ElementName.APP_ID,
                    enums.ElementName.DEVICE_OS,
                ]
                raise ValueError(f"Single str value is not supported by {name.value}. Name must be one of: {', '.join([n.value for n in allowed_names])}")

            if op not in allowed_ops:
                raise ValueError(f"Single str value and {name.value} are not supported by {op.value}. Operator must be one of: {', '.join([o.value for o in allowed_ops])}")

        if is_number(value):
            if name == enums.ElementName.APP_USER_PROPERTY:
                allowed_ops = list(enums.ElementOperatorBinary)
            elif name == enums.ElementName.APP_CUSTOM_SIGNAL:
                allowed_ops = list(enums.ElementOperatorBinary)
            else:
                allowed_names = [
                    enums.ElementName.APP_USER_PROPERTY,
                    enums.ElementName.APP_CUSTOM_SIGNAL,
                ]
                raise ValueError(f"Single number value is not supported by {name.value}. Name must be one of: {', '.join([n.value for n in allowed_names])}")

            if op not in allowed_ops:
                raise ValueError(f"Single number value and {name.value} are not supported by {op.value}. Operator must be one of: {', '.join([o.value for o in allowed_ops])}")

        if isinstance(value, datetime):
            if name == enums.ElementName.APP_FIRST_OPEN_TIMESTAMP:
                allowed_ops = [enums.ElementOperatorBinary.LTE, enums.ElementOperatorBinary.GT]
            elif name == enums.ElementName.DEVICE_DATETIME:
                allowed_ops = [enums.ElementOperatorBinary.LT, enums.ElementOperatorBinary.GTE]
            else:
                allowed_names = [
                    enums.ElementName.APP_FIRST_OPEN_TIMESTAMP,
                    enums.ElementName.DEVICE_DATETIME,
                ]
                raise ValueError(f"Single datetime value is not supported by {name.value}. Name must be one of: {', '.join([n.value for n in allowed_names])}")

            if op not in allowed_ops:
                raise ValueError(f"Single datetime value and {name.value} are not supported by {op.value}. Operator must be one of: {', '.join([o.value for o in allowed_ops])}")

    # multiple values
    elif values is not None:
        values_contain_number = (values and any([is_number(v) for v in values])) or is_number(value)
        if values_contain_number:
            raise ValueError("Multiple number values are not supported")

        if name == enums.ElementName.APP_BUILD:
            allowed_ops = list(enums.ElementOperatorMethodString)
        elif name == enums.ElementName.APP_VERSION:
            allowed_ops = list(enums.ElementOperatorMethodString)
        elif name == enums.ElementName.APP_AUDIENCES:
            allowed_ops = list(enums.ElementOperatorMethodAudiences)
        elif name == enums.ElementName.APP_IMPORTED_SEGMENTS:
            allowed_ops = list(enums.ElementOperatorMethodAudiences)
        elif name == enums.ElementName.APP_USER_PROPERTY:
            allowed_ops = list(enums.ElementOperatorMethodString)
        elif name == enums.ElementName.APP_CUSTOM_SIGNAL:
            allowed_ops = list(enums.ElementOperatorMethodString)
        elif name == enums.ElementName.APP_FIREBASE_INSTALLATION_ID:
            allowed_ops = list(enums.ElementOperatorBinaryArray)
        elif name == enums.ElementName.DEVICE_COUNTRY:
            allowed_ops = list(enums.ElementOperatorBinaryArray)
        elif name == enums.ElementName.DEVICE_LANGUAGE:
            allowed_ops = list(enums.ElementOperatorBinaryArray)
        else:
            allowed_names = [
                enums.ElementName.APP_BUILD,
                enums.ElementName.APP_VERSION,
                enums.ElementName.APP_AUDIENCES,
                enums.ElementName.APP_IMPORTED_SEGMENTS,
                enums.ElementName.APP_FIREBASE_INSTALLATION_ID,
                enums.ElementName.APP_USER_PROPERTY,
                enums.ElementName.APP_CUSTOM_SIGNAL,
                enums.ElementName.DEVICE_COUNTRY,
                enums.ElementName.DEVICE_LANGUAGE,
            ]
            raise ValueError(f"Multiple str values are not supported by {name.value}. Name must be one of: {', '.join([n.value for n in allowed_names])}")

        if op not in allowed_ops:
            raise ValueError(f"Multiple str values and {name.value} are not supported by {op.value}. Operator must be one of: {', '.join([o.value for o in allowed_ops])}")

    else:
        raise ValueError("Must provide value or values")
