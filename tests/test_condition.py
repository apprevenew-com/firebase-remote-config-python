from datetime import datetime

import pytz

import firebase_remote_config.conditions as cond


def test_percent():
    c = cond.NamedCondition(
        name=__name__,
        condition=cond.PercentCondition(
            percent=50,
            percentOperator=cond.PercentConditionOperator.LESS_OR_EQUAL
        ),
    )
    assert str(c) == "percent <= 50"

    c = cond.NamedCondition(
        name=__name__,
        condition=cond.PercentCondition(
            percentRange=cond.PercentRange(lowerBound=0, upperBound=50),
            percentOperator=cond.PercentConditionOperator.BETWEEN
        ),
    )
    assert str(c) == "percent between 0 and 50"


def test_always():
    c = cond.NamedCondition(
        name=__name__,
        condition=cond.TrueCondition(),
    )
    assert str(c) == "true"


def test_builder():
    b = cond.ConditionBuilder()
    c = b.CONDITION().APP_CUSTOM_SIGNAL("custom_key").EQ(123).build()
    assert str(c) == "app.customSignal['custom_key'] == 123"

    b = cond.ConditionBuilder()
    c = b.CONDITION().APP_VERSION().GT("1.2.0").build()
    assert str(c) == "app.version.>(['1.2.0'])"

    b = cond.ConditionBuilder()
    c = b.CONDITION().DEVICE_DATETIME().GTE(datetime(2025, 1, 1, 10, 10, 42)).build()
    assert str(c) == "dateTime >= dateTime('2025-01-01T10:10:42')"

    b = cond.ConditionBuilder()
    c = b.CONDITION().APP_FIRST_OPEN_TIMESTAMP().LTE(datetime(2025, 1, 1, 10, 10, 42)).build()
    assert str(c) == "app.firstOpenTimestamp <= ('2025-01-01T10:10:42')"

    b = cond.ConditionBuilder()
    b.CONDITION().DEVICE_LANGUAGE().IN(["en-US"])
    b.PERCENT().LTE(50)
    b.CONDITION().APP_FIRST_OPEN_TIMESTAMP().LTE(datetime(2025, 1, 1, 10, 10, 42))
    b.CONDITION().DEVICE_COUNTRY().IN(["US"])
    c = b.build()
    assert str(c) == "device.language in ['en-US'] && percent <= 50 && app.firstOpenTimestamp <= ('2025-01-01T10:10:42') && device.country in ['US']"


def test_datetime_timezone():
    b = cond.ConditionBuilder()
    dt_tz_naive = datetime(2025, 1, 1, 10, 10, 42)
    dt_tz_aware = datetime(2025, 1, 1, 10, 10, 42).replace(tzinfo=pytz.UTC)
    b.CONDITION().DEVICE_DATETIME().GTE(dt_tz_naive)
    b.CONDITION().DEVICE_DATETIME().GTE(dt_tz_aware)
    c = b.build()
    assert str(c) == "dateTime >= dateTime('2025-01-01T10:10:42') && dateTime >= dateTime('2025-01-01T10:10:42', 'UTC')"


def test_element_app_build():
    b = cond.ConditionBuilder()
    b.CONDITION().APP_BUILD().GTE("1.0.0")
    b.CONDITION().APP_BUILD().CONTAINS(["1.0.0", "1.0.1"])
    c = b.build()
    assert str(c) == "app.build.>=(['1.0.0']) && app.build.contains(['1.0.0', '1.0.1'])"
