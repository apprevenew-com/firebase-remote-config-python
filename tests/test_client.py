from unittest.mock import MagicMock, patch

import pytest
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials as UserCredentials

from firebase_remote_config import RemoteConfigClient
from firebase_remote_config.exceptions import UnexpectedError

PROJECT_ID = "my-project"
BASE_URL = (
    "https://firebaseremoteconfig.googleapis.com/v1/projects/my-project/remoteConfig"
)


def _response(status_code=200, text='{"conditions": []}', etag="etag-1"):
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = text
    resp.headers = {"etag": etag}
    return resp


def _user_credentials():
    """MagicMock that passes isinstance checks for user ADC credentials."""
    creds = MagicMock(spec=UserCredentials)
    creds.quota_project_id = None
    creds.with_quota_project.return_value = creds
    return creds


def _service_account_credentials():
    creds = MagicMock(spec=service_account.Credentials)
    creds.with_quota_project.return_value = creds
    return creds


@patch("firebase_remote_config.client.AuthorizedSession")
def test_user_credentials_default_quota_to_project(mock_session_cls):
    creds = _user_credentials()

    RemoteConfigClient(creds, PROJECT_ID)

    # user ADC without an explicit quota project defaults to project_id, so the
    # RC REST API does not reject the request with 403 SERVICE_DISABLED.
    creds.with_quota_project.assert_called_once_with(PROJECT_ID)
    mock_session_cls.assert_called_once_with(creds)


@patch("firebase_remote_config.client.AuthorizedSession")
def test_explicit_quota_project_wins(mock_session_cls):
    creds = _user_credentials()

    RemoteConfigClient(creds, PROJECT_ID, quota_project_id="billing-project")

    creds.with_quota_project.assert_called_once_with("billing-project")


@patch("firebase_remote_config.client.AuthorizedSession")
def test_existing_quota_project_is_honored(mock_session_cls):
    creds = _user_credentials()
    creds.quota_project_id = "preset-project"

    RemoteConfigClient(creds, PROJECT_ID)

    creds.with_quota_project.assert_called_once_with("preset-project")


@patch("firebase_remote_config.client.AuthorizedSession")
def test_service_account_gets_no_quota_project(mock_session_cls):
    creds = _service_account_credentials()

    RemoteConfigClient(creds, PROJECT_ID)

    creds.with_quota_project.assert_not_called()
    mock_session_cls.assert_called_once_with(creds)


@patch("firebase_remote_config.client.AuthorizedSession")
def test_get_remote_config_success(mock_session_cls):
    session = mock_session_cls.return_value
    session.get.return_value = _response(etag="etag-42")

    client = RemoteConfigClient(_service_account_credentials(), PROJECT_ID)
    config = client.get_remote_config()

    assert config.etag == "etag-42"
    assert config.template.conditions == []
    session.get.assert_called_once_with(
        BASE_URL, headers={"Content-Type": "application/json; UTF8"}, params=None, timeout=30
    )


@patch("firebase_remote_config.client.AuthorizedSession")
def test_get_remote_config_with_version_number(mock_session_cls):
    session = mock_session_cls.return_value
    session.get.return_value = _response()

    client = RemoteConfigClient(_service_account_credentials(), PROJECT_ID)
    client.get_remote_config(version_number="7")

    _, kwargs = session.get.call_args
    assert kwargs["params"] == {"versionNumber": "7"}


@patch("firebase_remote_config.client.AuthorizedSession")
def test_get_remote_config_non_200_raises(mock_session_cls):
    session = mock_session_cls.return_value
    session.get.return_value = _response(status_code=403, text="denied")

    client = RemoteConfigClient(_service_account_credentials(), PROJECT_ID)
    with pytest.raises(UnexpectedError):
        client.get_remote_config()


@patch("firebase_remote_config.client.AuthorizedSession")
def test_rollback_posts_version(mock_session_cls):
    session = mock_session_cls.return_value
    session.post.return_value = _response()

    client = RemoteConfigClient(_service_account_credentials(), PROJECT_ID)
    client.rollback(version_number="42")

    args, kwargs = session.post.call_args
    assert args[0] == f"{BASE_URL}:rollback"
    assert '"versionNumber":"42"' in kwargs["data"].replace(" ", "")
    assert kwargs["timeout"] == 30


@patch("firebase_remote_config.client.AuthorizedSession")
def test_custom_timeout_forwarded(mock_session_cls):
    session = mock_session_cls.return_value
    session.get.return_value = _response()

    client = RemoteConfigClient(
        _service_account_credentials(), PROJECT_ID, timeout=5
    )
    client.get_remote_config()

    _, kwargs = session.get.call_args
    assert kwargs["timeout"] == 5
