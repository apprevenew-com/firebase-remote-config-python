import firebase_remote_config.conditions as cond


def test_basic():
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
    ]

    for case_str in test_cases_valid:
        condition = p.parse(case_str)
        passed = str(condition) == case_str

        try:
            assert passed
        except AssertionError as e:
            print("\nError!")
            raise AssertionError(f"ground: {case_str}, condition: {condition}") from e

def test_invalid_whitespace():
    p = cond.ConditionParser()

    test_cases_invalid = [
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

def test_get_grammar():
    grammar = cond.get_grammar()
    assert len(grammar) > 0
