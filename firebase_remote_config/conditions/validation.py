from typing import Dict, List

from . import enums


def supports_value_number(name: enums.ElementName, op: enums.ElementOperator) -> bool:
    """
    Check if an element supports a number value.
    :param ElementName name: The name of the element.
    :param ElementOperator op: The operator to check.
    """
    supported_dict = {
        enums.ElementName.APP_USER_PROPERTY: list(enums.ElementOperatorBinary),
        enums.ElementName.APP_CUSTOM_SIGNAL: list(enums.ElementOperatorBinary),
    }
    supported_ops = supported_dict.get(name)
    return supported_ops and op in supported_ops

def supports_value_str(name: enums.ElementName, op: enums.ElementOperator) -> bool:
    """
    Check if an element supports a string value.
    :param ElementName name: The name of the element.
    :param ElementOperator op: The operator to check.
    """
    return not supports_value_number(name, op)

def supports_key(name: enums.ElementName) -> bool:
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
        enums.ElementName.APP_AUDIENCES: list(enums.ElementOperatorAudiences),
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
    if isinstance(op, (enums.ElementOperatorMethodString, enums.ElementOperatorBinaryArray, enums.ElementOperatorAudiences)):
        return False
    raise ValueError(f"Unknown operator: {op}")


def needs_parentheses(op: enums.ElementOperator) -> bool:
    """
    Checks if an operator needs parentheses around its value.
    :param ElementOperator op: The operator to check.
    """
    return isinstance(op, (enums.ElementOperatorMethodString, enums.ElementOperatorMethodSemantic, enums.ElementOperatorAudiences))


def needs_dot(op: enums.ElementOperator) -> bool:
    """
    Checks if syntax requires a dot before operator.
    :param ElementOperator op: The operator to check.
    """
    return isinstance(op, (enums.ElementOperatorMethodString, enums.ElementOperatorMethodSemantic, enums.ElementOperatorAudiences))
