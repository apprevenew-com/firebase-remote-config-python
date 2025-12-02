from datetime import datetime
from enum import Enum
from typing import Union

# element names

class ElementName(Enum):
    """The name of an element."""
    APP_BUILD = "app.build"  # Evaluates to TRUE or FALSE based on an app's build number.
    APP_VERSION = "app.version"  # Evaluates to TRUE or FALSE based on an app's version number.
    APP_ID = "app.id"  # An element based on the app's Firebase App ID.
    APP_AUDIENCES = "app.audiences"  # Evaluates to TRUE or FALSE based on Firebase Analytics audience(s).
    APP_IMPORTED_SEGMENTS = "app.importedSegments"  # Evaluates to TRUE or FALSE based on whether user belongs to imported segments.
    APP_FIRST_OPEN_TIMESTAMP = "app.firstOpenTimestamp"  # Based on the first time a user launches an app.
    DEVICE_DATETIME = "dateTime"  # Based on the time of the last fetch (ISO format).
    APP_USER_PROPERTY = "app.userProperty"  # Evaluates based on Google Analytics User Property.
    # APP_OS_VERSION = "app.operatingSystemAndVersion"  # Based on OS and OS version (Web apps only).  # TODO: not supported
    # APP_BROWSER_VERSION = "app.browserAndVersion"  # Based on browser and version (Web apps only).  # TODO: not supported
    APP_FIREBASE_INSTALLATION_ID = "app.firebaseInstallationId"  # Based on specific Firebase installation IDs.
    APP_CUSTOM_SIGNAL = "app.customSignal"  # Evaluates based on custom signal conditions.
    DEVICE_COUNTRY = "device.country"  # Based on the device's region/country (ISO 3166-1 alpha-2).
    DEVICE_LANGUAGE = "device.language"  # Based on the device's selected language (IETF Language tag).
    DEVICE_OS = "device.os"  # Based on the operating system (Apple or Android).

    def __hash__(self):
        """ElementName can be used as a key in a dictionary."""
        return hash(self.name)

# operators

class ElementOperatorBinary(Enum):
    """Compares two values."""
    EQ = "=="  # Matches a value equal to the target value.
    GTE = ">="  # Matches a numeric value greater than or equal to the target value.
    GT = ">"  # Matches a numeric value greater than the target value.
    LTE = "<="  # Matches a numeric value less than or equal to the target value.
    LT = "<"  # Matches a numeric value less than the target value.
    NEQ = "!="  # Matches a value not equal to the target value.


class ElementOperatorMethodString(Enum):
    """Compares a value to a list of target string values."""
    CONTAINS = "contains"  # Matches if at least one of the target values is a substring of the actual custom value.
    CONTAINS_REGEX = "matches"  # The target regular expression matches at least one of the actual values (RE2 format).
    DOES_NOT_CONTAIN = "notContains"  # Matches if none of the target values is a substring of the actual custom value.
    EXACTLY_MATCHES = "exactlyMatches"  # Matches if the actual value exactly matches at least one of the target values.


class ElementOperatorMethodSemantic(Enum):
    """Compares a value to a list of target values following semantic versioning rules."""
    SEM_EQ = "=="  # Matches if the actual version value is equal to the target value.
    SEM_GTE = ">="  # Matches if the actual version value is greater than or equal to the target value.
    SEM_GT = ">"  # Matches if the actual version value is greater than the target value.
    SEM_LTE = "<="  # Matches if the actual version value is less than or equal to the target value.
    SEM_LT = "<"  # Matches if the actual version value is less than the target value.
    SEM_NEQ = "!="  # Matches if the actual version value is not equal to the target value.


class ElementOperatorBinaryArray(Enum):
    """Compares a value to a list of target values."""
    IN = "in"  # Matches if the actual value matches any specified in the list.


class ElementOperatorMethodAudiences(Enum):
    """Compares a value to a list of target audience names."""
    IN_AT_LEAST_ONE = "inAtLeastOne"  # Matches if the actual audience matches at least one audience name in the list.
    NOT_IN_AT_LEAST_ONE = "notInAtLeastOne"  # Matches if the actual audience does not match at least one audience name in the list.
    IN_ALL = "inAll"  # Matches if the actual audience is a member of every audience name in the list.
    NOT_IN_ALL = "notInAll"  # Matches if the actual audience is not a member of any audience in the list.


ElementOperator = Union[ElementOperatorBinary, ElementOperatorMethodString, ElementOperatorMethodSemantic, ElementOperatorBinaryArray, ElementOperatorMethodAudiences]


class PercentConditionOperator(Enum):
    """Checks if a value is in a given percentile range."""
    BETWEEN = "BETWEEN"  # Matches if the user percentage is between lower and upper bound
    GREATER_THAN = ">"  # Matches if the user percentage is greater than provided value
    LESS_OR_EQUAL = "<="  # Matches if the user percentage is less than or equal to provided value


CustomValue = Union[str, int, float, datetime]
