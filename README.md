# Firebase Remote Config SDK for Python

A Python SDK for managing Firebase Remote Config, built as a typed abstraction over the Firebase REST API.
This package provides a convenient way to get, validate, update and upload remote config templates.

## Features

- Provides SDK for managing Remote Config for mobile clients that is missing from Google `firebase-admin` package
- Type-safe interface using Pydantic models
- Minimal DSL for building and manipulating condition expressions
- Enables parsing condition expressions into Pydantic models

## Capabilities

- Fetch and update Remote Config templates
- Validate template updates before deployment
- List template versions and perform rollbacks
- Add, query, and update conditions and parameters
- Serialize and parse condition expressions to/from structured form

## Installation

```bash
pip install firebase-remote-config
```

## Requirements

- Python 3.9 or higher
- Firebase project with Remote Config enabled
- Service account credentials with necessary permissions (Firebase Admin / Firebase Remote Config Admin)

## Usage

### Getting Started

First, initialize the client with your Firebase credentials:

```python
from google.oauth2 import service_account
from firebase_remote_config import RemoteConfigClient

# Initialize the client
credentials = service_account.Credentials.from_service_account_file('path/to/service-account.json')
client = RemoteConfigClient(credentials, 'your-project-id')

# Get current Remote Config template
config = client.get_remote_config()

# Upload template to Firebase Remote Config
updated_config = client.update_remote_config(config)
```

### Use Cases


#### 1. Creating and Updating Parameters

```python
import firebase_remote_config as rc

# Add new parameter to the remote config template
new_param = rc.RemoteConfigParameter(
    defaultValue=rc.RemoteConfigParameterValue(value="default_value"),
    valueType=rc.ParameterValueType.STRING,
    description="A new parameter"
)
config.template.parameters["new_parameter"] = new_param

# find parameter in the template
param = config.get_parameter_by_key("new_parameter")
param.description = "My new parameter"
```


#### 2. Working with Conditional Values

```python
import firebase_remote_config as rc

# Create condition object
condition = rc.RemoteConfigCondition(
    name="ios_users",
    expression="device.os == 'ios'",
    tagColor=rc.TagColor.BLUE,
)

# Create condition in rconfig template
config.create_condition(condition)

# Use newly created condition in a conditional value
config.set_conditional_value(
    param_key="my_parameter",
    param_value=rc.RemoteConfigParameterValue(value="my_value"),
    param_value_type=rc.ParameterValueType.STRING,
    condition_name="ios_users",
)
```


#### 3. Building Complex Conditions with ConditionBuilder

```python
import firebase_remote_config as rc
from firebase_remote_config.conditions import ConditionBuilder

# Create a complex condition
builder = ConditionBuilder()
builder.CONDITION().APP_VERSION().GTE("1.2.0")
builder.CONDITION().APP_USER_PROPERTY("total_purchases_usd").GTE(5)
builder.CONDITION().DEVICE_COUNTRY().IN(["US", "CA"])
cond_expr = builder.build()

# Serialize condition as string
cond_expr_str = str(cond_expr)
# app.version.>=(['1.2.0']) && app.userProperty['total_purchases_usd'] >= 5 && device.country in ['US', 'CA']

# Create condition in remote config template
config.create_condition(rc.RemoteConfigCondition(
    name="active_premium_users",
    expression=cond_expr_str,
    tagColor=rc.TagColor.GREEN,
))
```


#### 4. Parsing condition expression

```python
from firebase_remote_config.conditions import ConditionParser

# Parse condition expression
parser = ConditionParser()
cond_expr = "dateTime >= dateTime('2025-01-01T09:00:00') && app.userProperty['my_property'].contains(['abc', 'def'])"
condition = parser.parse(cond_expr)

# Compare string representations of the condition to the original expression
print(str(condition) == cond_expr)
# True
```


#### 5. Version Management

```python
# List recent versions
versions, _ = client.list_versions(page_size=30)

# Rollback to a previous version
rolled_back_config = client.rollback(version_number="42")
```

## License

This project is licensed under the terms of the LICENSE file in the root of this repository.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
