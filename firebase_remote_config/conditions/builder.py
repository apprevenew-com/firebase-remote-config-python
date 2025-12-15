from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Union

from . import conditions as cond
from . import enums


def build_with_value(name: enums.ElementName, key: Optional[str], op: enums.ElementOperator, v: cond.CustomValue) -> cond.ElementCondition:
    return cond.ElementCondition(element=cond.Element(name=name, key=key), operator=op, value=v)


def build_with_values(name: enums.ElementName, key: Optional[str], op: enums.ElementOperator, xv: List[cond.CustomValue]) -> cond.ElementCondition:
    return cond.ElementCondition(element=cond.Element(name=name, key=key), operator=op, values=xv)


class ConditionAppender:
    builder_instance: ConditionBuilder

    def __init__(self, builder_instance: ConditionBuilder):
        self.builder_instance = builder_instance

    def _append(self, c: cond.AtomCondition) -> ConditionBuilder:
        if not self.builder_instance.conditions:
            self.builder_instance.conditions = []
        self.builder_instance.conditions.append(c)
        return self.builder_instance


class ConditionBuilder(ConditionAppender):
    """Builder instance to construct condition expressions."""
    conditions: List[cond.AtomCondition]

    def __init__(self):
        """Returns Builder instance to construct condition expression."""
        self.conditions = []
        super().__init__(self)

    def build(self) -> cond.Condition:
        """Returns condition expression for all conditions previously appended to this Builder instance."""
        return cond.AndCondition(conditions=self.conditions)

    def TRUE(self) -> ConditionBuilder:
        """Appends always true condition."""
        return self._append(cond.TrueCondition())

    def FALSE(self) -> ConditionBuilder:
        """Appends always false condition."""
        return self._append(cond.FalseCondition())

    def PERCENT(self):
        """Appends condition based on percentage randomly and persistently assigned to each user on a per-project basis."""
        return self._PERCENT(self)

    def CONDITION(self):
        """Appends custom element condition."""
        return self._CONDITION(self)

    class _PERCENT(ConditionAppender):
        def GT(self, percent: int) -> ConditionBuilder:
            """
            Matches when user percentage is greater than provided percent value.

            :param int percent: Percent value (0-100).
            Example: 50 for 50%
            """
            return self._append(cond.PercentCondition(percent=percent, percentOperator=enums.PercentConditionOperator.GREATER_THAN))

        def LTE(self, percent: int) -> ConditionBuilder:
            """
            Matches when user percentage is less than or equal to provided percent value.

            :param int percent: Percent value (0-100).
            Example: 25 for 25%
            """
            return self._append(cond.PercentCondition(percent=percent, percentOperator=enums.PercentConditionOperator.LESS_OR_EQUAL))

        def BETWEEN(self, lower: int, upper: int) -> ConditionBuilder:
            """
            Matches when user percentage is between lower and upper bounds.

            :param int lower: Lower bound (0-100).
            :param int upper: Upper bound (0-100).
            Example: lower=20, upper=40 for 20-40%
            """
            return self._append(cond.PercentCondition(percentRange=cond.PercentRange(lowerBound=lower, upperBound=upper), percentOperator=enums.PercentConditionOperator.BETWEEN))

    class _CONDITION(ConditionAppender):

        def APP_VERSION(self):
            """Appends condition based on app version."""
            return self._APP_VERSION(self.builder_instance)

        def APP_BUILD(self):
            """Appends condition based on app build."""
            return self._APP_BUILD(self.builder_instance)

        def APP_ID(self):
            """Appends condition based on app id."""
            return self._APP_ID(self.builder_instance)

        def APP_AUDIENCES(self):
            """Appends condition based on app Google Analytics audiences."""
            return self._APP_AUDIENCES(self.builder_instance)

        def APP_IMPORTED_SEGMENTS(self):
            """Appends condition based on app imported segments."""
            return self._APP_IMPORTED_SEGMENTS(self.builder_instance)

        def APP_FIRST_OPEN_TIMESTAMP(self):
            """Appends condition based on app first open timestamp."""
            return self._APP_FIRST_OPEN_TIMESTAMP(self.builder_instance)

        def DEVICE_DATETIME(self):
            """Appends condition based on device datetime."""
            return self._DEVICE_DATETIME(self.builder_instance)

        def APP_USER_PROPERTY(self, key: str):
            """
            Appends condition based on the value of the Google Analytics user property.
            :param str key: The key of the Google Analytics user property.
            Example: "user_property_key"
            """
            return self._APP_USER_PROPERTY(self.builder_instance, key)

        def APP_CUSTOM_SIGNAL(self, key: str):
            """
            Appends condition based on the value of the Google Analytics custom signal.
            :param str key: The key of the custom signal.
            Example: "user_custom_signal_key"
            """
            return self._APP_CUSTOM_SIGNAL(self.builder_instance, key)

        def APP_FIREBASE_INSTALLATION_ID(self):
            """Appends condition based on the app's Firebase installation id."""
            return self._APP_FIREBASE_INSTALLATION_ID(self.builder_instance)

        def DEVICE_COUNTRY(self):
            """Appends condition based on the country."""
            return self._DEVICE_COUNTRY(self.builder_instance)

        def DEVICE_LANGUAGE(self):
            """Appends condition based on the language."""
            return self._DEVICE_LANGUAGE(self.builder_instance)

        def DEVICE_OS(self):
            """Appends condition based on the device operating system."""
            return self._DEVICE_OS(self.builder_instance)

        class _APP_VERSION(ConditionAppender):
            element = enums.ElementName.APP_VERSION
            key = None

            def EQ(self, s: str) -> ConditionBuilder:
                """
                Matches when app version is equal to provided version.
                :param str s: Version value.
                Example: "1.2.3"
                """
                return self._append(build_with_value(self.element, self.key, enums.ElementOperatorMethodSemantic.SEM_EQ, s))

            def GTE(self, s: str) -> ConditionBuilder:
                """
                Matches when app version is greater than or semantically equal to provided version.
                :param str s: Version value.
                Example: "2.0.1"
                """
                return self._append(build_with_value(self.element, self.key, enums.ElementOperatorMethodSemantic.SEM_GTE, s))

            def GT(self, s: str) -> ConditionBuilder:
                """
                Matches when app version is semantically greater than provided version.
                :param str s: Version value.
                Example: "2.0.1"
                """
                return self._append(build_with_value(self.element, self.key, enums.ElementOperatorMethodSemantic.SEM_GT, s))

            def LTE(self, s: str) -> ConditionBuilder:
                """
                Matches when app version is less than or semantically equal to provided version.
                :param str s: Version value.
                Example: "2.0.1"
                """
                return self._append(build_with_value(self.element, self.key, enums.ElementOperatorMethodSemantic.SEM_LTE, s))

            def LT(self, s: str) -> ConditionBuilder:
                """
                Matches when app version is semantically less than provided version.
                :param str s: Version value.
                Example: "2.0.1"
                """
                return self._append(build_with_value(self.element, self.key, enums.ElementOperatorMethodSemantic.SEM_LT, s))

            def NEQ(self, s: str) -> ConditionBuilder:
                """
                Matches when app version is not equal to provided version.
                :param str s: Version value.
                Example: "2.0.1"
                """
                return self._append(build_with_value(self.element, self.key, enums.ElementOperatorMethodSemantic.SEM_NEQ, s))

            def CONTAINS(self, xs: List[str]) -> ConditionBuilder:
                """
                Matches when app version contains provided strings.
                :param List[str] xs: Strings to match against.
                Example: ["2.0.", "1.5.2"]
                """
                return self._append(build_with_values(self.element, self.key, enums.ElementOperatorMethodString.CONTAINS, xs))

            def CONTAINS_REGEX(self, xs: List[str]) -> ConditionBuilder:
                """
                Matches when app version matches provided regex.
                :param List[str] xs: Regex strings to match against.
                Example: ["^1\\.", "^2\\."]
                """
                return self._append(build_with_values(self.element, self.key, enums.ElementOperatorMethodString.CONTAINS_REGEX, xs))

            def DOES_NOT_CONTAIN(self, xs: List[str]) -> ConditionBuilder:
                """
                Matches when app version does not contain provided strings.
                :param List[str] xs: Strings to match against.
                Example: ["1.2.", "1.3.0"]
                """
                return self._append(build_with_values(self.element, self.key, enums.ElementOperatorMethodString.DOES_NOT_CONTAIN, xs))

            def EXACTLY_MATCHES(self, xs: List[str]) -> ConditionBuilder:
                """
                Matches when app version exactly matches provided strings.
                :param List[str] xs: Strings to match against.
                Example: ["1.5.2"]
                """
                return self._append(build_with_values(self.element, self.key, enums.ElementOperatorMethodString.EXACTLY_MATCHES, xs))

        class _APP_BUILD(ConditionAppender):
            element = enums.ElementName.APP_BUILD
            key = None

            def EQ(self, s: str) -> ConditionBuilder:
                """
                Matches when app build is equal to provided build.
                :param str s: Build identifier.
                Example: "2025.1.1.42"
                """
                return self._append(build_with_value(self.element, self.key, enums.ElementOperatorMethodSemantic.SEM_EQ, s))

            def GTE(self, s: str) -> ConditionBuilder:
                """
                Matches when app build is semantically greater than or equal to provided build.
                :param str s: Build identifier.
                Example: "2025.1.1.42"
                """
                return self._append(build_with_value(self.element, self.key, enums.ElementOperatorMethodSemantic.SEM_GTE, s))

            def GT(self, s: str) -> ConditionBuilder:
                """
                Matches when app build is semantically greater than provided build.
                :param str s: Build identifier.
                Example: "2025.1.1.42"
                """
                return self._append(build_with_value(self.element, self.key, enums.ElementOperatorMethodSemantic.SEM_GT, s))

            def LTE(self, s: str) -> ConditionBuilder:
                """
                Matches when app build is less than or semantically equal to provided build.
                :param str s: Build identifier.
                Example: "2025.1.1.42"
                """
                return self._append(build_with_value(self.element, self.key, enums.ElementOperatorMethodSemantic.SEM_LTE, s))

            def LT(self, s: str) -> ConditionBuilder:
                """
                Matches when app build is semantically less than provided build.
                :param str s: Build identifier.
                Example: "2025.1.1.42"
                """
                return self._append(build_with_value(self.element, self.key, enums.ElementOperatorMethodSemantic.SEM_LT, s))

            def NEQ(self, s: str) -> ConditionBuilder:
                """
                Matches when app build is not equal to provided build.
                :param str s: Build identifier.
                Example: "2025.1.1.42"
                """
                return self._append(build_with_value(self.element, self.key, enums.ElementOperatorMethodSemantic.SEM_NEQ, s))

            def CONTAINS(self, xs: List[str]) -> ConditionBuilder:
                """
                Matches when app build contains provided strings.
                :param List[str] xs: Strings to match against.
                Example: ["2025.1.1"]
                """
                return self._append(build_with_values(self.element, self.key, enums.ElementOperatorMethodString.CONTAINS, xs))

            def CONTAINS_REGEX(self, xs: List[str]) -> ConditionBuilder:
                """
                Matches when app build matches provided regex.
                :param List[str] xs: Regex strings to match against.
                Example: ["^2025\\."]
                """
                return self._append(build_with_values(self.element, self.key, enums.ElementOperatorMethodString.CONTAINS_REGEX, xs))

            def DOES_NOT_CONTAIN(self, xs: List[str]) -> ConditionBuilder:
                """
                Matches when app build does not contain provided strings.
                :param List[str] xs: Strings to match against.
                Example: ["2025.1.1"]
                """
                return self._append(build_with_values(self.element, self.key, enums.ElementOperatorMethodString.DOES_NOT_CONTAIN, xs))

            def EXACTLY_MATCHES(self, xs: List[str]) -> ConditionBuilder:
                """
                Matches when app build exactly matches provided strings.
                :param List[str] xs: Strings to match against.
                Example: ["2025.1.1"]
                """
                return self._append(build_with_values(self.element, self.key, enums.ElementOperatorMethodString.EXACTLY_MATCHES, xs))

        class _APP_ID(ConditionAppender):
            element = enums.ElementName.APP_ID
            key = None

            def EQ(self, s: str) -> ConditionBuilder:
                """
                Matches when app id is equal to provided id.
                :param str s: App id.
                Example: "com.example.app"
                """
                return self._append(build_with_value(self.element, self.key, enums.ElementOperatorBinary.EQ, s))

        class _APP_AUDIENCES(ConditionAppender):
            element = enums.ElementName.APP_AUDIENCES
            key = None

            def IN_AT_LEAST_ONE(self, xs: List[str]) -> ConditionBuilder:
                """
                Matches when app audiences contains at least one of provided audiences.
                :param List[str] xs: Audiences to match against.
                Example: ["high_value_users", "new_users"]
                """
                return self._append(build_with_values(self.element, self.key, enums.ElementOperatorMethodAudiences.IN_AT_LEAST_ONE, xs))

            def NOT_IN_AT_LEAST_ONE(self, xs: List[str]) -> ConditionBuilder:
                """
                Matches when app audiences does not contain at least one of provided audiences.
                :param List[str] xs: Audiences to match against.
                Example: ["inactive_users", "churned_users"]
                """
                return self._append(build_with_values(self.element, self.key, enums.ElementOperatorMethodAudiences.NOT_IN_AT_LEAST_ONE, xs))

            def IN_ALL(self, xs: List[str]) -> ConditionBuilder:
                """
                Matches when app audiences contains all of provided audiences.
                :param List[str] xs: Audiences to match against.
                Example: ["premium_users", "active_users"]
                """
                return self._append(build_with_values(self.element, self.key, enums.ElementOperatorMethodAudiences.IN_ALL, xs))

            def NOT_IN_ALL(self, xs: List[str]) -> ConditionBuilder:
                """
                Matches when app audiences does not contain all of provided audiences.
                :param List[str] xs: Audiences to match against.
                Example: ["beta_testers", "early_adopters"]
                """
                return self._append(build_with_values(self.element, self.key, enums.ElementOperatorMethodAudiences.NOT_IN_ALL, xs))

        class _APP_IMPORTED_SEGMENTS(ConditionAppender):
            element = enums.ElementName.APP_IMPORTED_SEGMENTS
            key = None

            def IN_AT_LEAST_ONE(self, xs: List[str]) -> ConditionBuilder:
                """
                Matches when user belongs to at least one of the imported segments.
                :param List[str] xs: Imported segments to match against.
                Example: ["high_value_users", "new_users"]
                """
                return self._append(build_with_values(self.element, self.key, enums.ElementOperatorMethodAudiences.IN_AT_LEAST_ONE, xs))

            def NOT_IN_AT_LEAST_ONE(self, xs: List[str]) -> ConditionBuilder:
                """
                Matches when user does not belong to at least one of the imported segments.
                :param List[str] xs: Imported segments to match against.
                Example: ["inactive_users", "churned_users"]
                """
                return self._append(build_with_values(self.element, self.key, enums.ElementOperatorMethodAudiences.NOT_IN_AT_LEAST_ONE, xs))

            def IN_ALL(self, xs: List[str]) -> ConditionBuilder:
                """
                Matches when user belongs to all of the imported segments.
                :param List[str] xs: Imported segments to match against.
                Example: ["premium_users", "active_users"]
                """
                return self._append(build_with_values(self.element, self.key, enums.ElementOperatorMethodAudiences.IN_ALL, xs))

            def NOT_IN_ALL(self, xs: List[str]) -> ConditionBuilder:
                """
                Matches when user does not belong to all of the imported segments.
                :param List[str] xs: Imported segments to match against.
                Example: ["beta_testers", "early_adopters"]
                """
                return self._append(build_with_values(self.element, self.key, enums.ElementOperatorMethodAudiences.NOT_IN_ALL, xs))

        class _APP_FIRST_OPEN_TIMESTAMP(ConditionAppender):
            element = enums.ElementName.APP_FIRST_OPEN_TIMESTAMP
            key = None

            def GT(self, dt: datetime) -> ConditionBuilder:
                """
                Matches when app first open timestamp is greater than provided timestamp.
                :param datetime dt: Timestamp.
                Example: datetime(2025, 1, 1, 10, 10, 0)
                """
                return self._append(build_with_value(self.element, self.key, enums.ElementOperatorBinary.GT, dt))

            def LTE(self, dt: datetime) -> ConditionBuilder:
                """
                Matches when app first open timestamp is less than or equal to provided timestamp.
                :param datetime dt: Timestamp.
                Example: datetime(2025, 1, 1, 10, 10, 0)
                """
                return self._append(build_with_value(self.element, self.key, enums.ElementOperatorBinary.LTE, dt))

        class _DEVICE_DATETIME(ConditionAppender):
            element = enums.ElementName.DEVICE_DATETIME
            key = None

            def GTE(self, dt: datetime) -> ConditionBuilder:
                """
                Matches when device datetime is greater than or equal to provided timestamp.
                :param datetime dt: Timestamp.
                Example: datetime(2025, 1, 1, 10, 10, 0)
                """
                return self._append(build_with_value(self.element, self.key, enums.ElementOperatorBinary.GTE, dt))

            def LT(self, dt: datetime) -> ConditionBuilder:
                """
                Matches when device datetime is less than provided timestamp.
                :param datetime dt: Timestamp.
                Example: datetime(2025, 1, 1, 10, 10, 0)
                """
                return self._append(build_with_value(self.element, self.key, enums.ElementOperatorBinary.LT, dt))

        class _APP_USER_PROPERTY(ConditionAppender):
            element = enums.ElementName.APP_USER_PROPERTY
            key: str

            def __init__(self, builder_instance: ConditionBuilder, key: str):
                super().__init__(builder_instance)
                self.key = key

            def EQ(self, v: Union[int, float]) -> ConditionBuilder:
                """
                Matches when app user property is equal to provided numeric value.
                :param Union[int, float] v: Numeric value.
                Example: 42 or 3.14
                """
                return self._append(build_with_value(self.element, self.key, enums.ElementOperatorBinary.EQ, v))

            def GTE(self, v: Union[int, float]) -> ConditionBuilder:
                """
                Matches when app user property is greater than or equal to provided numeric value.
                :param Union[int, float] v: Numeric value.
                Example: 42 or 3.14
                """
                return self._append(build_with_value(self.element, self.key, enums.ElementOperatorBinary.GTE, v))

            def GT(self, v: Union[int, float]) -> ConditionBuilder:
                """
                Matches when app user property is greater than provided numeric value.

                :param Union[int, float] v: Numeric value.
                Example: 42 or 3.14
                """
                return self._append(build_with_value(self.element, self.key, enums.ElementOperatorBinary.GT, v))

            def LTE(self, v: Union[int, float]) -> ConditionBuilder:
                """
                Matches when app user property is less than or equal to provided numeric value.
                :param Union[int, float] v: Numeric value.
                Example: 42 or 3.14
                """
                return self._append(build_with_value(self.element, self.key, enums.ElementOperatorBinary.LTE, v))

            def LT(self, v: Union[int, float]) -> ConditionBuilder:
                """
                Matches when app user property is less than provided numeric value.
                :param Union[int, float] v: Numeric value.
                Example: 42 or 3.14
                """
                return self._append(build_with_value(self.element, self.key, enums.ElementOperatorBinary.LT, v))

            def NEQ(self, v: Union[int, float]) -> ConditionBuilder:
                """
                Matches when app user property is not equal to provided numeric value.
                :param Union[int, float] v: Numeric value.
                Example: 42 or 3.14
                """
                return self._append(build_with_value(self.element, self.key, enums.ElementOperatorBinary.NEQ, v))

            def CONTAINS(self, xs: List[str]) -> ConditionBuilder:
                """
                Matches when app user property contains provided strings.
                :param List[str] xs: Strings to match against.
                Example: ["premium", "vip"]
                """
                return self._append(build_with_values(self.element, self.key, enums.ElementOperatorMethodString.CONTAINS, xs))

            def CONTAINS_REGEX(self, xs: List[str]) -> ConditionBuilder:
                """
                Matches when app user property contains provided regex.
                :param List[str] xs: Regex strings to match against.
                Example: ["^premium.*", "^vip.*"]
                """
                return self._append(build_with_values(self.element, self.key, enums.ElementOperatorMethodString.CONTAINS_REGEX, xs))

            def DOES_NOT_CONTAIN(self, xs: List[str]) -> ConditionBuilder:
                """
                Matches when app user property does not contain provided strings.
                :param List[str] xs: Strings to match against.
                Example: ["inactive", "blocked"]
                """
                return self._append(build_with_values(self.element, self.key, enums.ElementOperatorMethodString.DOES_NOT_CONTAIN, xs))

            def EXACTLY_MATCHES(self, xs: List[str]) -> ConditionBuilder:
                """
                Matches when app user property exactly matches provided strings.
                :param List[str] xs: Strings to match against.
                Example: ["premium", "vip"]
                """
                return self._append(build_with_values(self.element, self.key, enums.ElementOperatorMethodString.EXACTLY_MATCHES, xs))

        class _APP_CUSTOM_SIGNAL(_APP_USER_PROPERTY):
            def __init__(self, builder_instance: ConditionBuilder, key: str):
                super().__init__(builder_instance, key)
                self.element = enums.ElementName.APP_CUSTOM_SIGNAL

        class _APP_FIREBASE_INSTALLATION_ID(ConditionAppender):
            element = enums.ElementName.APP_FIREBASE_INSTALLATION_ID
            key = None

            def IN(self, xs: List[str]) -> ConditionBuilder:
                """
                Matches when app firebase installation id is in provided list.
                :param List[str] xs: List of installation ids to match against.
                Example: ["fcm-123", "fcm-456"]
                """
                return self._append(build_with_values(self.element, self.key, enums.ElementOperatorBinaryArray.IN, xs))

        class _DEVICE_COUNTRY(ConditionAppender):
            element = enums.ElementName.DEVICE_COUNTRY
            key = None

            def IN(self, xs: List[str]) -> ConditionBuilder:
                """
                Matches when device country is in provided list.
                :param List[str] xs: List of countries (2-letter codes) to match against.
                Example: ["US", "GB", "DE"]
                """
                return self._append(build_with_values(self.element, self.key, enums.ElementOperatorBinaryArray.IN, xs))

        class _DEVICE_LANGUAGE(ConditionAppender):
            element = enums.ElementName.DEVICE_LANGUAGE
            key = None

            def IN(self, xs: List[str]) -> ConditionBuilder:
                """
                Matches when device language is in provided list.
                :param List[str] xs: List of languages to match against.
                Example: ["en-US", "en-GB", "es-ES", "fr-FR", "de-DE"]
                """
                return self._append(build_with_values(self.element, self.key, enums.ElementOperatorBinaryArray.IN, xs))

        class _DEVICE_OS(ConditionAppender):
            element = enums.ElementName.DEVICE_OS
            key = None

            def EQ(self, s: str) -> ConditionBuilder:
                """
                Matches when device os is equal to provided os.
                :param str s: Os.
                Example: "ios" or "android"
                """
                return self._append(build_with_value(self.element, self.key, enums.ElementOperatorBinary.EQ, s))

            def NEQ(self, s: str) -> ConditionBuilder:
                """
                Matches when device os is not equal to provided os.
                :param str s: Os.
                Example: "ios" or "android"
                """
                return self._append(build_with_value(self.element, self.key, enums.ElementOperatorBinary.NEQ, s))
