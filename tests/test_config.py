import firebase_remote_config as rc


def get_config():
    config = rc.RemoteConfig(
        template=rc.RemoteConfigTemplate(
            conditions=[
                rc.RemoteConfigCondition(
                    name="condition_1",
                    expression="app.version.>(['1.0.0'])",
                    tagColor=rc.TagColor.GREEN,
                ),
                rc.RemoteConfigCondition(
                    name="condition_2",
                    expression="device.language in ['en-US', 'de-DE']",
                    tagColor=rc.TagColor.BLUE,
                ),
            ],
            parameters={
                "test_param_1": rc.RemoteConfigParameter(
                    defaultValue=rc.RemoteConfigParameterValue(value="test_value_1_default"),
                    conditionalValues={
                        "condition_1": rc.RemoteConfigParameterValue(value="test_value_1_c1"),
                        "condition_2": rc.RemoteConfigParameterValue(value="test_value_1_c2"),
                    },
                    valueType=rc.ParameterValueType.STRING,
                ),
            },
            parameterGroups={
                "pg1": rc.RemoteConfigParameterGroup(
                    parameters={
                        "test_param_2": rc.RemoteConfigParameter(
                            defaultValue=rc.RemoteConfigParameterValue(value="test_value_2_default"),
                            valueType=rc.ParameterValueType.STRING,
                        ),
                        "test_param_3": rc.RemoteConfigParameter(
                            defaultValue=rc.RemoteConfigParameterValue(value="test_value_3_default"),
                            valueType=rc.ParameterValueType.STRING,
                        ),
                    },
                ),
            },
        ),
        etag="test",
    )
    return config


def test_iterate():
    config = get_config()

    # interate over conditions
    assert len(list(config.iterate_conditions())) == 2

    # iterate over parameters
    assert len(list(config.iterate_parameter_items())) == 3


def test_crd():
    config = get_config()

    # insert new condition

    config.insert_condition(
        rc.RemoteConfigCondition(
            name="new_condition",
            expression="device.os == 'ios'",
        ),
    )

    assert len(config.template.conditions) == 3
    assert config.template.conditions[0].name == "new_condition"
    assert config.template.conditions[1].name == "condition_1"
    assert config.template.conditions[2].name == "condition_2"

    # set conditional values

    config.set_conditional_value(
        "test_param_1",
        rc.RemoteConfigParameterValue(value="new_test_value"),
        rc.ParameterValueType.STRING,
        "new_condition",
    )

    config.set_conditional_value(
        "new_test_param",
        rc.RemoteConfigParameterValue(value="new_test_value"),
        rc.ParameterValueType.STRING,
        "new_condition",
    )

    assert config.template.parameters["test_param_1"].conditionalValues["new_condition"].value == "new_test_value"

    # remove condition and check that condition values are also removed

    config.remove_conditions(["new_condition"])

    assert len(config.template.conditions) == 2
    assert config.template.conditions[0].name == "condition_1"
    assert config.template.conditions[1].name == "condition_2"

    assert len(config.template.parameters["test_param_1"].conditionalValues.values()) == 2
    assert config.template.parameters["new_test_param"].conditionalValues == {}
