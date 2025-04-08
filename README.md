# Firebase Remote Config Admin SDK for Python

A Python SDK for managing Firebase Remote Config via REST API. This package provides a convenient way to interact with Firebase Remote Config programmatically.

## Features

- Get and update Remote Config templates
- Validate Remote Config changes before deployment
- List and rollback to previous versions
- Full support for all Remote Config features including parameters, conditions, and version management
- Type-safe with Pydantic models

## Installation

```bash
pip install firebase-admin-rconfig
```

## Requirements

- Python 3.9 or higher
- Firebase project with Remote Config enabled
- Service account credentials with Firebase Remote Config Admin permissions

## Usage

### Getting Started

First, initialize the client with your Firebase credentials:

```python
from google.oauth2 import service_account
from firebase_admin_rconfig import RemoteConfigClient

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
from firebase_admin_rconfig import RemoteConfigParameter, TagColor

# Add new parameter to the remote config template
new_param = RemoteConfigParameter(
    defaultValue=RemoteConfigParameterValue(value="default_value"),
    valueType=ParameterValueType.STRING,
    description="A new parameter"
)
config.template.parameters["new_parameter"] = new_param

# find parameter in the template
param = config.find_param_by_key("new_parameter")
param.description = "My new parameter"
```

#### 2. Working with Conditional Values

```python
from firebase_admin_rconfig import RemoteConfigCondition, TagColor

# Create condition object
condition = RemoteConfigCondition(
    name="ios_users",
    expression="device.os == 'ios'",
    tagColor=TagColor.BLUE,
)

# Insert condition to rconfig template
config.insert_condition(condition)

# Use newly created condition in a conditional value
config.set_conditional_value(
    param_key="my_parameter",
    param_value=RemoteConfigParameterValue(value="my_value"),
    param_value_type=ParameterValueType.STRING,
    condition_name="ios_users",
)
```

#### 3. Building Complex Conditions with ConditionBuilder

```python
from datetime import datetime
from firebase_admin_rconfig.conditions import ConditionBuilder
from firebase_admin_rconfig import RemoteConfigCondition, TagColor

# Create a complex condition
builder = ConditionBuilder()
builder.APP_VERSION().GTE("2.0.0")
builder.CONDITION().APP_USER_PROPERTY("total_purchases_usd").LTE(5)
builder.CONDITION().DEVICE_COUNTRY().IN(["US", "CA", "GB"])
cond_expr = builder.build()

# Serialize condition as string
cond_expr_str = str(cond_expr)

# Insert condition to remote config template
config.insert_condition(RemoteConfigCondition(
    name="active_premium_users",
    expression=cond_expr_str,
    tagColor=TagColor.GREEN,
))

# Set conditional values
feature_param.set_conditional_value(
    param_value=RemoteConfigParameterValue(value="true"),
    param_value_type=ParameterValueType.BOOLEAN,
    condition_name="holiday_promotion",
)
```

#### 4. Version Management

```python
from firebase_admin_rconfig.models import ListVersionsParameters

# List recent versions
versions, _ = client.list_versions(page_size=30)

# Rollback to a previous version
from firebase_admin_rconfig.models import RollbackRequest

rolled_back_config = client.rollback("42")
```

## License

This project is licensed under the terms of the LICENSE file in the root of this repository.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
