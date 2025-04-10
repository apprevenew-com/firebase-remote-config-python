from datetime import datetime
from typing import Dict, Optional

import google.auth.transport.requests
import requests
from google.oauth2 import service_account

from . import exceptions
from .models import (
    ListVersionsParameters,
    ListVersionsResponse,
    RemoteConfig,
    RemoteConfigResponse,
    RemoteConfigTemplate,
    RollbackRequest,
)

FIREBASE_REMOTE_CONFIG_URL = "https://firebaseremoteconfig.googleapis.com/v1/projects"


class RemoteConfigClient:
    def __init__(self, credentials: service_account.Credentials, project_id: str):
        self.credentials = credentials
        self.url = f"{FIREBASE_REMOTE_CONFIG_URL}/{project_id}/remoteConfig"

    def _call_get_remote_config(self, version_number: Optional[str] = None) -> requests.Response:
        access_token = get_oauth_token(self.credentials)
        headers = make_headers(access_token)

        if version_number is not None:
            params = {"versionNumber": version_number}
        else:
            params = None

        response = requests.request(method="get", url=self.url, headers=headers, params=params)
        return response

    def _call_update_remote_config(self, rc: RemoteConfig, validate_only: bool) -> requests.Response:
        url = self.url
        if validate_only:
            url = f"{self.url}?validate_only=true"

        access_token = get_oauth_token(self.credentials)
        headers = make_headers(access_token, rc.etag)

        data = rc.template.model_dump_json(exclude_none=True)
        response = requests.request(
            method="put", url=url, headers=headers, data=data
        )

        return response

    def _call_list_versions(self, params: ListVersionsParameters) -> requests.Response:
        access_token = get_oauth_token(self.credentials)
        headers = make_headers(access_token)
        params_dict = params.model_dump(exclude_none=True)

        response = requests.request(method="get", url=f"{self.url}:listVersions", headers=headers, params=params_dict)
        return response

    def _call_rollback(self, request: RollbackRequest) -> requests.Response:
        access_token = get_oauth_token(self.credentials)
        headers = make_headers(access_token)

        data = request.model_dump_json(exclude_none=True)
        response = requests.request(method="post", url=f"{self.url}:rollback", headers=headers, data=data)
        return response

    # API methods

    def get_remote_config(self, version_number: Optional[str] = None) -> RemoteConfig:
        response = self._call_get_remote_config(version_number)
        if response.status_code != 200:
            raise exceptions.UnexpectedError(f"Unexpected error: {response.text}")
        return make_remote_config(response)

    def validate_remote_config(self, rc: RemoteConfig) -> RemoteConfig:
        response = self._call_update_remote_config(rc, validate_only=True)
        if response.status_code != 200:
            rc_error = RemoteConfigResponse.model_validate_json(response.text)
            rc_error.error.raise_error()
        return make_remote_config(response)

    def update_remote_config(self, rc: RemoteConfig) -> RemoteConfig:
        response = self._call_update_remote_config(rc, validate_only=False)
        if response.status_code != 200:
            rc_error = RemoteConfigResponse.model_validate_json(response.text)
            rc_error.error.raise_error()
        return make_remote_config(response)

    def list_versions(
            self,
            page_size: Optional[int] = None,
            page_token: Optional[str] = None,
            end_version_number: Optional[str] = None,
            start_time: Optional[datetime] = None,
            end_time: Optional[datetime] = None,
    ) -> ListVersionsResponse:
        params = ListVersionsParameters(
            pageSize=page_size,
            pageToken=page_token,
            endVersionNumber=end_version_number,
            startTime=start_time,
            endTime=end_time,
        )
        response = self._call_list_versions(params)

        if response.status_code != 200:
            raise exceptions.UnexpectedError(f"Unexpected error: {response.text}")

        return ListVersionsResponse.model_validate_json(response.text)

    def rollback(self, version_number: str) -> RemoteConfig:
        response = self._call_rollback(RollbackRequest(versionNumber=version_number))
        if response.status_code != 200:
            raise exceptions.UnexpectedError(f"Unexpected error: {response.text}")
        return make_remote_config(response)


# Utils

def make_remote_config(response: requests.Response) -> RemoteConfig:
    template = RemoteConfigTemplate.model_validate_json(response.text)
    etag = response.headers["etag"]
    return RemoteConfig(template=template, etag=etag)

def get_oauth_token(credentials: service_account.Credentials) -> Optional[str]:
    if not credentials.token or credentials.expired:
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)

    return credentials.token


def make_headers(access_token: str, etag: Optional[str] = None) -> Dict:
    headers = {
        "Content-Type": "application/json; UTF8",
        "Authorization": f"Bearer {access_token}",
    }

    if etag:
        headers["If-Match"] = etag

    return headers
