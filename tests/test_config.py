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


def test_get():
    config = get_config()

    assert config.get_condition_by_name("condition_1").name == "condition_1"
    assert config.get_condition_by_name("condition_2").name == "condition_2"
    assert config.get_parameter_by_key("test_param_1").defaultValue.value == "test_value_1_default"
    assert config.get_parameter_by_key("test_param_2").defaultValue.value == "test_value_2_default"
    assert config.get_parameter_by_key("test_param_3").defaultValue.value == "test_value_3_default"


def test_crd():
    config = get_config()

    # insert new condition

    config.create_condition(
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
        "new_condition",
    )

    config.create_empty_parameter(
        "new_test_param",
        rc.ParameterValueType.STRING,
    )

    config.set_conditional_value(
        "new_test_param",
        rc.RemoteConfigParameterValue(value="new_test_value"),
        "new_condition",
    )

    assert config.template.parameters["test_param_1"].conditionalValues["new_condition"].value == "new_test_value"
    assert config.template.parameters["new_test_param"].conditionalValues["new_condition"].value == "new_test_value"

    # remove conditional value

    config.remove_conditional_value("test_param_1", ["new_condition"], skip_missing=False)
    assert "new_condition" not in config.template.parameters["test_param_1"].conditionalValues

    # remove condition and check that condition values are also removed

    config.remove_conditions(["new_condition"])

    assert len(config.template.conditions) == 2
    assert config.template.conditions[0].name == "condition_1"
    assert config.template.conditions[1].name == "condition_2"

    assert len(config.template.parameters["test_param_1"].conditionalValues.values()) == 2
    assert config.template.parameters["new_test_param"].conditionalValues == {}


def test_replace_condition():
    config = get_config()

    # replace condition

    config.replace_condition(
        "condition_2",
        rc.RemoteConfigCondition(
            name="replaced_condition",
            expression="device.os == 'android'",
        ),
    )

    assert len(config.template.conditions) == 2
    assert config.template.conditions[0].name == "condition_1"
    assert config.template.conditions[1].name == "replaced_condition"
    assert config.template.conditions[1].expression == "device.os == 'android'"

    # check that conditional values are replaced
    cv = config.template.parameters["test_param_1"].conditionalValues
    assert "condition_2" not in cv
    assert cv["replaced_condition"].value == "test_value_1_c2"


def test_no_parameters():
    # this is a valid config even if there are no parameters
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
            parameterGroups={
                "pg1": rc.RemoteConfigParameterGroup(
                    parameters={
                        "test_param_1": rc.RemoteConfigParameter(
                            defaultValue=rc.RemoteConfigParameterValue(value="test_value_1_default"),
                            valueType=rc.ParameterValueType.STRING,
                        ),
                        "test_param_2": rc.RemoteConfigParameter(
                            defaultValue=rc.RemoteConfigParameterValue(value="test_value_2_default"),
                            valueType=rc.ParameterValueType.STRING,
                        ),
                    },
                ),
            },
        ),
        etag="test",
    )
    assert len(config.template.parameterGroups) == 1

    parameter_names = [param_key for param_key, _ in config.iterate_parameter_items()]
    assert len(parameter_names) == 2
    assert "test_param_1" in parameter_names
    assert "test_param_2" in parameter_names

    # this is a valid config even if there are no parameter groups
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
                    valueType=rc.ParameterValueType.STRING,
                ),
                "test_param_2": rc.RemoteConfigParameter(
                    defaultValue=rc.RemoteConfigParameterValue(value="test_value_2_default"),
                    valueType=rc.ParameterValueType.STRING,
                ),
            },
        ),
        etag="test",
    )
    assert len(config.template.parameterGroups) == 0

    parameter_names = [param_key for param_key, _ in config.iterate_parameter_items()]
    assert len(parameter_names) == 2
    assert "test_param_1" in parameter_names
    assert "test_param_2" in parameter_names


def test_value_to_type():
    assert rc.value_to_type("test") == rc.ParameterValueType.STRING
    assert rc.value_to_type("true") == rc.ParameterValueType.STRING
    assert rc.value_to_type("false") == rc.ParameterValueType.STRING
    assert rc.value_to_type("123") == rc.ParameterValueType.STRING
    assert rc.value_to_type("1.0") == rc.ParameterValueType.STRING

    assert rc.value_to_type('{"key": "value"}') == rc.ParameterValueType.JSON
    assert rc.value_to_type('{"key": true, "key2": {"key3": 123}}') == rc.ParameterValueType.JSON

    assert rc.value_to_type(1) == rc.ParameterValueType.NUMBER
    assert rc.value_to_type(-1) == rc.ParameterValueType.NUMBER

    assert rc.value_to_type(1.0) == rc.ParameterValueType.NUMBER
    assert rc.value_to_type(-1.0) == rc.ParameterValueType.NUMBER

    assert rc.value_to_type(True) == rc.ParameterValueType.BOOLEAN
    assert rc.value_to_type(False) == rc.ParameterValueType.BOOLEAN


def test_value_str():
    assert rc.value_to_str("test") == "test"

    assert rc.value_to_str(1) == "1"
    assert rc.value_to_str(-1) == "-1"

    assert rc.value_to_str(1.0) == "1.0"
    assert rc.value_to_str(-1.0) == "-1.0"

    assert rc.value_to_str(True) == "true"
    assert rc.value_to_str(False) == "false"
