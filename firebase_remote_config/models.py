import json
from datetime import datetime
from enum import Enum
from itertools import chain
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

from pydantic import BaseModel, Field, field_serializer

from . import exceptions

# Models for Firebase Remote Config REST API

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


# https://firebase.google.com/docs/reference/remote-config/rest/v1/RemoteConfig#conditiondisplaycolor
class TagColor(Enum):
    CONDITION_DISPLAY_COLOR_UNSPECIFIED = "CONDITION_DISPLAY_COLOR_UNSPECIFIED"
    BLUE = "BLUE"
    BROWN = "BROWN"
    CYAN = "CYAN"
    DEEP_ORANGE = "DEEP_ORANGE"
    GREEN = "GREEN"
    INDIGO = "INDIGO"
    LIME = "LIME"
    ORANGE = "ORANGE"
    PINK = "PINK"
    PURPLE = "PURPLE"
    TEAL = "TEAL"


# https://firebase.google.com/docs/reference/remote-config/rest/v1/RemoteConfig#remoteconfigcondition
class RemoteConfigCondition(BaseModel):
    name: str
    expression: str
    tagColor: Optional[TagColor] = None


# https://firebase.google.com/docs/reference/remote-config/rest/v1/RemoteConfig#remoteconfigparametervalue
# must contain only one of the fields (union type)
class RemoteConfigParameterValue(BaseModel):
    value: Optional[str] = None
    useInAppDefault: Optional[bool] = None
    personalizationValue: Optional[Any] = None
    rolloutValue: Optional[Any] = None


# https://firebase.google.com/docs/reference/remote-config/rest/v1/RemoteConfig#parametervaluetype
class ParameterValueType(Enum):
    PARAMETER_VALUE_TYPE_UNSPECIFIED = "PARAMETER_VALUE_TYPE_UNSPECIFIED"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    NUMBER = "NUMBER"
    JSON = "JSON"


# https://firebase.google.com/docs/reference/remote-config/rest/v1/RemoteConfig#remoteconfigparameter
class RemoteConfigParameter(BaseModel):
    defaultValue: Optional[RemoteConfigParameterValue] = None
    conditionalValues: Optional[Dict[str, RemoteConfigParameterValue]] = None
    description: Optional[str] = None
    valueType: ParameterValueType

    def remove_conditional_values(self, condition_names: List[str]) -> None:
        """
        Remove conditional values by their condition names.
        :param condition_names List[str]: List of condition names to remove.
        """
        if not self.conditionalValues:
            return

        self.conditionalValues = {key: c for key, c in self.conditionalValues.items() if key not in condition_names}

    def set_conditional_value(self, param_value: RemoteConfigParameterValue, condition_name: str, overwrite: bool = True) -> None:
        """
        Set a conditional value for a parameter.
        :param param_value RemoteConfigParameterValue: Parameter value.
        :param condition_name str: Condition name.
        :param overwrite Optional[bool]: Sets behavior when the parameter already has a conditional value with given condition name. True = overwrite, False = raise Exception.
        Raises:
            ConditionalValueAlreadySetError: If the parameter already has a conditional value with the given condition name and overwrite is False.
        """
        if not self.conditionalValues:
            self.conditionalValues = {}

        if condition_name in self.conditionalValues and not overwrite:
            raise exceptions.ConditionalValueAlreadySetError(f"Conditional value for {condition_name} already set")

        self.conditionalValues[condition_name] = param_value


# https://firebase.google.com/docs/reference/remote-config/rest/v1/RemoteConfig#RemoteConfigParameterGroup
class RemoteConfigParameterGroup(BaseModel):
    description: Optional[str] = None
    parameters: Optional[Dict[str, RemoteConfigParameter]] = Field(default_factory=dict)


# https://firebase.google.com/docs/reference/remote-config/rest/v1/Version#RemoteConfigUser
class RemoteConfigUser(BaseModel):
    name: Optional[str] = None
    email: str
    imageUrl: Optional[str] = None


# https://firebase.google.com/docs/reference/remote-config/rest/v1/Version#RemoteConfigUpdateOrigin
class RemoteConfigUpdateOrigin(Enum):
    UPDATE_ORIGIN_UNSPECIFIED = "UPDATE_ORIGIN_UNSPECIFIED"
    CONSOLE = "CONSOLE"
    REST_API = "REST_API"
    SDK = "SDK"


# https://firebase.google.com/docs/reference/remote-config/rest/v1/Version#RemoteConfigUpdateType
class RemoteConfigUpdateType(Enum):
    REMOTE_CONFIG_UPDATE_TYPE_UNSPECIFIED = "REMOTE_CONFIG_UPDATE_TYPE_UNSPECIFIED"
    INCREMENTAL_UPDATE = "INCREMENTAL_UPDATE"
    FORCED_UPDATE = "FORCED_UPDATE"
    ROLLBACK = "ROLLBACK"


# https://firebase.google.com/docs/reference/remote-config/rest/v1/Version
class Version(BaseModel):
    versionNumber: Optional[str] = None
    updateTime: Optional[datetime] = None
    updateUser: Optional[RemoteConfigUser] = None
    description: Optional[str] = None
    updateOrigin: Optional[RemoteConfigUpdateOrigin] = None
    updateType: Optional[RemoteConfigUpdateType] = None
    rollbackSource: Optional[str] = None
    isLegacy: Optional[bool] = None


# https://firebase.google.com/docs/reference/remote-config/rest/v1/projects.remoteConfig/listVersions
class ListVersionsResponse(BaseModel):
    versions: List[Version]
    nextPageToken: Optional[str] = None


# https://firebase.google.com/docs/reference/remote-config/rest/v1/RemoteConfig
class RemoteConfigTemplate(BaseModel):
    conditions: List[RemoteConfigCondition]
    parameters: Optional[Dict[str, RemoteConfigParameter]] = Field(default_factory=dict)
    version: Optional[Version] = None
    parameterGroups: Optional[Dict[str, RemoteConfigParameterGroup]] = Field(default_factory=dict)


# https://firebase.google.com/docs/reference/remote-config/rest/v1/projects.remoteConfig/listVersions#query-parameters
class ListVersionsParameters(BaseModel):
    pageSize: Optional[int] = Field(None, ge=1, le=100)
    pageToken: Optional[str] = None
    endVersionNumber: Optional[str] = None
    startTime: Optional[datetime] = None
    endTime: Optional[datetime] = None

    @field_serializer("startTime", "endTime")
    def serialize_dt(self, dt: datetime) -> str:
        return dt.strftime(DATETIME_FORMAT)


# https://firebase.google.com/docs/reference/remote-config/rest/v1/projects.remoteConfig/rollback#request-body
class RollbackRequest(BaseModel):
    versionNumber: str

# Custom classes

class RemoteConfigError(BaseModel):
    """Error model for Remote Config API responses."""
    code: int
    message: str
    status: str

    def raise_error(self) -> None:
        if self.code == 400:
            if "VERSION_MISMATCH" in self.message:
                raise exceptions.VersionMismatchError(f"Version mismatch: {self.message}")
            else:
                raise exceptions.ValidationError(f"Validation error: {self.message}")
        else:
            raise exceptions.UnexpectedError(f"Unexpected error: {self.message}")

class RemoteConfigResponse(BaseModel):
    """Response model for Remote Config API responses."""
    error: Optional[RemoteConfigError] = None

class RemoteConfig(BaseModel):
    """Main config model."""
    template: RemoteConfigTemplate
    etag: str

    def create_condition(self, condition: RemoteConfigCondition, insert_after_condition: Optional[str] = None) -> None:
        """
        Create a new condition.
        :param condition RemoteConfigCondition: Condition to create.
        :param insert_after_condition Optional[str]: Condition name after which to insert the new condition.
        """
        existing_conditions = self.template.conditions
        existing_conditions_names = [c.name for c in existing_conditions]

        if condition.name in existing_conditions_names:
            # TODO: warn, ignore or update?
            raise exceptions.ConditionAlreadyExistsError(f"Condition {condition.name} already exists")

        if insert_after_condition:
            # insert after condition with the provided name
            try:
                split_ix = existing_conditions_names.index(insert_after_condition)
                self.template.conditions = [
                    *self.template.conditions[:split_ix + 1],
                    condition,
                    *self.template.conditions[split_ix + 1:],
                ]
            except ValueError as e:  # could not find condition name
                raise exceptions.ConditionNotFoundError(f"Condition {insert_after_condition} not found") from e

        else:
            # push on top of the conditions list
            self.template.conditions = [
                condition,
                *existing_conditions,
            ]

    def remove_conditions(self, condition_names: List[str]) -> None:
        """
        Remove conditions by their names.
        :param condition_names List[str]: List of condition names to remove.
        """
        self.template.conditions = [c for c in self.template.conditions if c.name not in condition_names]

        # after deleting conditions we need to clean up orphan params
        for _, param in self.iterate_parameter_items():
            param.remove_conditional_values(condition_names)

    def set_conditional_value(
            self,
            param_key: str,
            param_value: RemoteConfigParameterValue,
            condition_name: str,
            overwrite: Optional[bool] = True,
    ) -> None:
        """
        Set a conditional value for a parameter.
        :param param_key str: Parameter key.
        :param param_value RemoteConfigParameterValue: Parameter value.
        :param condition_name str: Condition name.
        :param overwrite Optional[bool]: Sets behavior when the parameter already has a conditional value with given condition name. True = overwrite, False = raise Exception.
        Raises:
            ParameterNotFoundError: If the parameter is not found.
            ConditionalValueAlreadySetError: If the parameter already has a conditional value with the given condition name and overwrite is False.
        """
        param = self.get_parameter_by_key(param_key)
        if not param:
            raise exceptions.ParameterNotFoundError(f"Parameter {param_key} not found")

        param.set_conditional_value(param_value, condition_name, overwrite)

    def remove_conditional_value(self, param_key: str, condition_names: List[str], skip_missing: bool = False) -> None:
        """
        Remove conditional values by their condition names.
        :param param_key str: Parameter key.
        :param condition_names List[str]: List of condition names to remove.
        :param skip_missing Optional[bool]: Sets behavior when the parameter is not found. True = skip, False = raise Exception.
        Raises:
            ParameterNotFoundError: If the parameter is not found and skip_missing is False.
        """
        param = self.get_parameter_by_key(param_key)
        if not param and not skip_missing:
            raise exceptions.ParameterNotFoundError(f"Parameter {param_key} not found")

        param.remove_conditional_values(condition_names)

    def create_empty_parameter(
        self,
        param_key: str,
        param_value_type: ParameterValueType,
        param_descr: Optional[str] = None,
        param_group_key: Optional[str] = None,
    ) -> RemoteConfigParameter:
        """
        Create an empty parameter.
        :param param_key str: Parameter key.
        :param param_value_type ParameterValueType: Parameter value type.
        :param param_descr Optional[str]: Parameter description.
        :param param_group_key Optional[str]: Parameter group key.
        """
        if param_key in self.template.parameters:
            raise exceptions.ParameterAlreadyExistsError(f"Parameter {param_key} already exists")

        if param_value_type == ParameterValueType.BOOLEAN:
            default_value = "false"
        elif param_value_type == ParameterValueType.NUMBER:
            default_value = "0"
        elif param_value_type == ParameterValueType.JSON:
            default_value = "{}"
        else:
            default_value = ""

        param = RemoteConfigParameter(
            conditionalValues={},
            defaultValue=RemoteConfigParameterValue(value=default_value),
            description=param_descr or f"Parameter {param_key}",
            valueType=param_value_type,
        )

        if param_group_key is None:
            # create outside parameter groups
            self.template.parameters[param_key] = param
        else:
            # set in parameter group
            param_group = self.template.parameterGroups.get(param_group_key)
            if not param_group:
                # create parameter group if not exists
                param_group = RemoteConfigParameterGroup(parameters={})
                self.template.parameterGroups[param_group_key] = param_group
            param_group.parameters[param_key] = param

        return param

    def iterate_parameter_items(self) -> Iterator[Tuple[str, RemoteConfigParameter]]:
        """
        Iterates over all parameters (with keys) in the config template.
        """
        for tpl in chain(self.template.parameters.items(), *[pg.parameters.items() for pg in self.template.parameterGroups.values()]):
            yield tpl

    def iterate_conditions(self) -> Iterator[RemoteConfigCondition]:
        """
        Iterates over all conditions in the config template.
        """
        for condition in self.template.conditions:
            yield condition

    def get_parameter_by_key(self, key: str) -> Optional[RemoteConfigParameter]:
        """
        Gets a parameter by its key.
        :param key str: Parameter key.
        :return Optional[RemoteConfigParameter]: Parameter object or None if not found.
        """
        return next((param for (param_key, param) in self.iterate_parameter_items() if param_key == key), None)

    def get_condition_by_name(self, name: str) -> Optional[RemoteConfigCondition]:
        """
        Gets a condition by its name.
        :param name str: Condition name.
        :return Optional[RemoteConfigCondition]: Condition object or None if not found.
        """
        return next((c for c in self.iterate_conditions() if c.name == name), None)

    def replace_condition(self, name: str, new_condition: RemoteConfigCondition, ignore_missing: bool = True) -> None:
        """
        Replaces a condition with a given name by a new condition.
        :param name str: Condition name.
        :param new_condition RemoteConfigCondition: New condition to replace with.
        :param ignore_missing bool: If True, does not raise an exception if the condition is not found.
        Raises:
            ConditionNotFoundError: If the condition is not found and ignore_missing is False.
        """
        condition = self.get_condition_by_name(name)
        if not condition and not ignore_missing:
            raise exceptions.ConditionNotFoundError(f"Condition {name} not found")

        self.template.conditions = [new_condition if c.name == name else c for c in self.template.conditions]

        if name == new_condition.name:
            return

        # replace all conditional values of the old condition with the new condition
        for _, param in self.iterate_parameter_items():
            if not param.conditionalValues:
                continue

            cond_value = param.conditionalValues.get(name)
            if not cond_value:
                continue

            param.remove_conditional_values([name])
            param.set_conditional_value(cond_value, new_condition.name)


# helper utils

def is_number(v: Union[str, int, float, bool]) -> bool:
    """
    Checks if the value is a number.
    :param v Union[str, int, float, bool]: Value to check.
    :return bool: True if the value is a number, False otherwise.
    """
    return type(v) is int or type(v) is float


def is_json(v: Union[str, int, float, bool]) -> bool:
    """
    Checks if the value is a JSON object.
    :param v Union[str, int, float, bool]: Value to check.
    :return bool: True if the value is a JSON object, False otherwise.
    """
    if type(v) is not str:
        return False
    try:
        res = json.loads(v)
        if type(res) is dict:
            return True
    except ValueError:  # json decoding failed
        pass

    return False


def is_str(v: Union[str, int, float, bool]) -> bool:
    """
    Checks if the value is a string (JSON string is not considered a string).
    :param v Union[str, int, float, bool]: Value to check.
    :return bool: True if the value is a string, False otherwise.
    """
    if type(v) is not str:
        return False
    return not is_json(v)


def is_bool(v: Union[str, int, float, bool]) -> bool:
    """
    Checks if the value is a boolean.
    :param v Union[str, int, float, bool]: Value to check.
    :return bool: True if the value is a boolean, False otherwise.
    """
    return type(v) is bool


def value_to_type(v: Union[str, int, float, bool]) -> ParameterValueType:
    """
    Converts a value to a parameter value type.
    :param v Union[str, int, float, bool]: Value to convert.
    :return ParameterValueType: Parameter value type.
    """
    if is_number(v):
        value_type = ParameterValueType.NUMBER
    elif is_bool(v):
        value_type = ParameterValueType.BOOLEAN
    elif is_json(v):
        value_type = ParameterValueType.JSON
    elif is_str(v):
        value_type = ParameterValueType.STRING
    else:
        raise ValueError(f"Unknown value type: {type(v)}")
    return value_type


def value_to_str(v: Union[str, int, float, bool]) -> str:
    """
    Converts a value to a string.
    :param v Union[str, int, float, bool]: Value to convert.
    :return str: String representation of the value.
    """
    if type(v) is bool:
        return "true" if v else "false"
    return str(v)
