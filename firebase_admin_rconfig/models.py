import json
from datetime import datetime
from enum import Enum
from itertools import chain
from typing import Any, Dict, Iterator, List, Optional, Union

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
        if not self.conditionalValues:
            return
        self.conditionalValues = {key: c for key, c in self.conditionalValues.items() if key not in condition_names}

    def set_conditional_value(self, param_value: RemoteConfigParameterValue, param_value_type: ParameterValueType, condition_name: str) -> None:
        if self.valueType != param_value_type:
            raise exceptions.WrongValueTypeError(f"Wrong value type. Existing type: {self.valueType.name}, new type: {param_value_type.name}")

        if not self.conditionalValues:
            self.conditionalValues = {}

        if condition_name in self.conditionalValues:
            # TODO: just warn if already exists?
            raise exceptions.ConditionalValueAlreadySetError(f"Conditional value for {condition_name} already set")

        self.conditionalValues[condition_name] = param_value


# https://firebase.google.com/docs/reference/remote-config/rest/v1/RemoteConfig#RemoteConfigParameterGroup
class RemoteConfigParameterGroup(BaseModel):
    description: Optional[str] = None
    parameters: Dict[str, RemoteConfigParameter]


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
    parameters: Dict[str, RemoteConfigParameter]
    version: Optional[Version] = None
    parameterGroups: Dict[str, RemoteConfigParameterGroup]


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

class RemoteConfigError(BaseModel):
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
    error: Optional[RemoteConfigError] = None

# Internal remote config class
class RemoteConfig(BaseModel):
    template: RemoteConfigTemplate
    etag: str

    def insert_condition(self, condition: RemoteConfigCondition, insert_after_condition: Optional[str] = None) -> None:
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
        self.template.conditions = [c for c in self.template.conditions if c.name not in condition_names]

        # after deleting conditions we need to clean up orphan params
        for param in self.iterate_params():
            param.remove_conditional_values(condition_names)

    def set_conditional_value(self, param_key: str, param_value: RemoteConfigParameterValue, param_value_type: ParameterValueType, condition_name: str) -> None:
        param = self.find_param_by_key(param_key)

        if not param:
            param = self.create_empty_parameter(param_key, param_value_type)

        param.set_conditional_value(param_value, param_value_type, condition_name)

    def create_empty_parameter(
        self,
        param_key: str,
        param_value_type: ParameterValueType,
        param_descr: Optional[str] = None,
        param_group_key: Optional[str] = None,
    ) -> RemoteConfigParameter:
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

    def find_param_by_key(self, key: str) -> Optional[RemoteConfigParameter]:
        # search in parameters
        param = self.template.parameters.get(key)

        # search in parameter groups
        for pg in self.template.parameterGroups.values():
            param = param or pg.parameters.get(key)

        return param

    def find_condition_by_name(self, condition_name: str) -> Optional[RemoteConfigCondition]:
        return next((c for c in self.iterate_conditions() if c.name == condition_name), None)

    def iterate_params(self) -> Iterator[RemoteConfigParameter]:
        for param in chain(self.template.parameters.values(), *[pg.parameters.values() for pg in self.template.parameterGroups.values()]):
            yield param

    def iterate_conditions(self) -> Iterator[RemoteConfigCondition]:
        for condition in self.template.conditions:
            yield condition

# helper utils

def is_number(v: Union[str, int, float, bool]) -> bool:
    return type(v) is int or type(v) is float


def is_json(v: Union[str, int, float, bool]) -> bool:
    if type(v) is not str:
        return False
    try:
        json.loads(v)
        return True
    except ValueError:  # json decoding failed
        return False


def is_str(v: Union[str, int, float, bool]) -> bool:
    if type(v) is not str:
        return False
    return not is_json(v)


def is_bool(v: Union[str, int, float, bool]) -> bool:
    return type(v) is bool


def value_to_type(v: Union[str, int, float, bool]) -> ParameterValueType:
    if is_number(v):
        value_type = ParameterValueType.NUMBER
    elif is_bool(v):
        value_type = ParameterValueType.BOOLEAN
    elif is_str(v):
        value_type = ParameterValueType.STRING
    elif is_json(v):
        value_type = ParameterValueType.JSON
    else:
        raise ValueError(f"Unknown value type: {type(v)}")
    return value_type


def value_to_str(v: Union[str, int, float, bool]) -> str:
    if type(v) is bool:
        return "true" if v else "false"
    return str(v)
