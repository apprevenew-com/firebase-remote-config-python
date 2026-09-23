from datetime import timedelta

import firebase_remote_config.conditions as cond
import firebase_remote_config.conditions.enums as enums


def test_valid_conditions():
    p = cond.ConditionParser()

    test_cases_valid = [
        "false && true",
        "app.userProperty['hello'].contains(['abc', 'def']) && app.userProperty['bye'] >= 2",
        "percent('seeeeeed') between 0 and 20 && app.id == 'my-app-id'",
        "app.customSignal['mykey'].notContains(['123']) && percent > 50",
        "dateTime >= dateTime('2025-01-01T09:00:00')",
        "app.firstOpenTimestamp <= ('2025-01-01T09:00:00')",
        "app.build.>=(['1.0.0']) && app.version.contains(['1.0.', '2.1.0'])",
        "device.language in ['en-US', 'RU'] && device.country in ['GB', 'AU', 'CA']",
        "dateTime < dateTime('2025-01-01T09:02:30') && dateTime >= dateTime('2025-01-01T09:02:30', 'UTC')",
        # numeric user property / custom signal values: zero, decimals, negatives
        "app.userProperty['count_purchases'] > 0",
        "app.userProperty['amount'] == 0",
        "app.userProperty['amount'] <= 3.99",
        "app.userProperty['ratio'] < 0.5",
        "app.userProperty['delta'] >= -2",
        "app.userProperty['delta'] != -0.25",
        "app.customSignal['score'] > 1.5 && app.userProperty['bucket'] == 1",
        # IANA timezones keep their name
        "app.firstOpenTimestamp > ('2025-10-01T00:00:00', 'Europe/Lisbon')",
        "app.firstOpenTimestamp <= ('2025-07-02T00:00:00', 'Asia/Bangkok')",
        "app.firstOpenTimestamp > ('2025-10-01T00:00:00', 'Etc/GMT')",
        "dateTime >= dateTime('2025-01-01T09:02:30', 'America/New_York')",
    ]

    for case_str in test_cases_valid:
        try:
            condition = p.parse(case_str)
            passed = str(condition) == case_str
        except Exception as e:
            raise ValueError(f"Error parsing {case_str}") from e

        try:
            assert passed
        except AssertionError as e:
            print("\nError!")
            raise AssertionError(f"ground: {case_str}, condition: {condition}") from e

def test_invalid_conditions():
    p = cond.ConditionParser()

    test_cases_invalid = [
        # invalid element / operator / value combinations
        "device.country == 'US'",
        "dateTime < ('2025-01-01T09:02:30')",
        "app.firstOpenTimestamp <= dateTime('2025-01-01T09:02:30')",
        "app.version.>=('1.0.1')",
        "app.version >= '1.0.1'",
        "app.version >= (['1.0.1'])",
        "app.userProperty['hello'] == 'def'",
        "app.userProperty['hello'].=='def'",
        "app.userProperty['hello'].==('def')",
        "app.userProperty['hello'].contains([123])",

        # invalid whitespace
        "app.userProperty['hello'] .contains(['abc', 'def'])",
        "app.userProperty['hello']. contains(['abc', 'def'])",
        "app.version.>= (['1.0.0'])",
        "app.version. >= (['1.0.0'])",
    ]

    for case_str in test_cases_invalid:
        try:
            condition = p.parse(case_str)
            passed = True
        except Exception:
            passed = False

        if passed:
            raise AssertionError(f"Parsed invalid condition {case_str} into {str(condition)}")


def test_numeric_values_keep_type():
    p = cond.ConditionParser()

    cases = [
        ("app.userProperty['x'] > 0", 0, int),
        ("app.userProperty['x'] == 0", 0, int),
        ("app.userProperty['x'] <= 3.99", 3.99, float),
        ("app.userProperty['x'] < 0.5", 0.5, float),
        ("app.userProperty['x'] >= -2", -2, int),
    ]

    for case_str, value, value_type in cases:
        element = p.parse(case_str).conditions[0]
        assert element.value == value, case_str
        assert type(element.value) is value_type, case_str


def test_timezone_offsets_are_correct():
    p = cond.ConditionParser()

    cases = [
        # (expression, expected UTC offset in hours)
        ("app.firstOpenTimestamp > ('2025-07-01T00:00:00', 'Europe/Lisbon')", 1),  # WEST
        ("app.firstOpenTimestamp > ('2025-01-01T00:00:00', 'Europe/Lisbon')", 0),  # WET
        ("app.firstOpenTimestamp > ('2025-01-01T00:00:00', 'Asia/Bangkok')", 7),
        ("app.firstOpenTimestamp > ('2025-01-01T00:00:00', 'Etc/GMT')", 0),
    ]

    for case_str, hours in cases:
        value = p.parse(case_str).conditions[0].value
        assert value.utcoffset() == timedelta(hours=hours), case_str


def test_get_grammar_method():
    grammar = cond.get_grammar()
    assert len(grammar) > 0

    expr = cond.get_grammar_element(enums.ElementName.APP_FIRST_OPEN_TIMESTAMP.value, enums.ElementOperatorBinary.GT.value)
    assert expr == "{'app.firstOpenTimestamp' '>'} {'(' {string enclosed in \"'\" [',' string enclosed in \"'\"]} ')'}"

    expr = cond.get_grammar_element(enums.ElementName.APP_FIRST_OPEN_TIMESTAMP.value, enums.ElementOperatorBinary.GTE.value)
    assert expr is None
