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
        "dateTime < dateTime('2025-01-01T09:02:30') && dateTime >= dateTime('2025-01-01T09:02:30', 'UTC')"
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


def test_get_grammar_method():
    grammar = cond.get_grammar()
    assert len(grammar) > 0

    expr = cond.get_grammar_element(enums.ElementName.APP_FIRST_OPEN_TIMESTAMP.value, enums.ElementOperatorBinary.GT.value)
    assert expr == "{'app.firstOpenTimestamp' '>'} {'(' {string enclosed in \"'\" [',' string enclosed in \"'\"]} ')'}"

    expr = cond.get_grammar_element(enums.ElementName.APP_FIRST_OPEN_TIMESTAMP.value, enums.ElementOperatorBinary.GTE.value)
    assert expr is None
