from datetime import datetime
from typing import Dict, Optional, Tuple, Union

import requests
from google.auth.credentials import Credentials, CredentialsWithQuotaProject
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.credentials import Credentials as UserCredentials

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

# Default per-request timeout (seconds). Overridable via the client ctor.
DEFAULT_TIMEOUT = 30

Timeout = Union[float, Tuple[float, float]]


class RemoteConfigClient:
    """Client for the Firebase Remote Config REST API.

    Authentication goes through google-auth's ``AuthorizedSession``, so any
    Application Default Credentials work: a service account, workload identity,
    or local user credentials from ``gcloud auth application-default login``.
    The session refreshes tokens automatically and attaches the
    ``x-goog-user-project`` quota-project header when the credentials carry a
    quota project.

    The Remote Config REST API rejects **user** credentials that have no quota
    project with ``403 SERVICE_DISABLED``. To keep that flow working out of the
    box, user credentials without an explicit quota project default to
    ``project_id``. Service-account / workload-identity credentials carry their
    own project, so no quota project is attached for them.
    """

    def __init__(
        self,
        credentials: Credentials,
        project_id: str,
        quota_project_id: Optional[str] = None,
        timeout: Timeout = DEFAULT_TIMEOUT,
    ):
        """Initialize the client.

        Args:
            credentials: Any google-auth credentials (service account, workload
                identity, or user ADC).
            project_id: Firebase / GCP project id that owns the Remote Config.
            quota_project_id: Explicit ``x-goog-user-project`` billing/quota
                project. When ``None``, it is resolved from the credentials
                (see ``_resolve_quota_project``).
            timeout: Per-request timeout in seconds, forwarded to ``requests``.
        """
        self.project_id = project_id
        self.url = f"{FIREBASE_REMOTE_CONFIG_URL}/{project_id}/remoteConfig"
        self.timeout = timeout

        quota_project = self._resolve_quota_project(
            credentials, project_id, quota_project_id
        )
        if quota_project is not None and isinstance(
            credentials, CredentialsWithQuotaProject
        ):
            credentials = credentials.with_quota_project(quota_project)

        self.credentials = credentials
        self.session = AuthorizedSession(credentials)

    @staticmethod
    def _resolve_quota_project(
        credentials: Credentials,
        project_id: str,
        quota_project_id: Optional[str],
    ) -> Optional[str]:
        """Pick the quota project for the ``x-goog-user-project`` header.

        An explicit ``quota_project_id`` always wins. Otherwise only **user**
        credentials need one: honor a quota project they already carry, else
        fall back to the target ``project_id``. Service-account /
        workload-identity credentials get ``None``.
        """
        if quota_project_id is not None:
            return quota_project_id
        if isinstance(credentials, UserCredentials):
            return getattr(credentials, "quota_project_id", None) or project_id
        return None

    def _call_get_remote_config(self, version_number: Optional[str] = None) -> requests.Response:
        headers = make_headers()

        if version_number is not None:
            params = {"versionNumber": version_number}
        else:
            params = None

        return self.session.get(
            self.url, headers=headers, params=params, timeout=self.timeout
        )

    def _call_update_remote_config(self, rc: RemoteConfig, validate_only: bool) -> requests.Response:
        url = self.url
        if validate_only:
            url = f"{self.url}?validate_only=true"

        headers = make_headers(rc.etag)
        data = rc.template.model_dump_json(exclude_none=True)
        return self.session.put(
            url, headers=headers, data=data, timeout=self.timeout
        )

    def _call_list_versions(self, params: ListVersionsParameters) -> requests.Response:
        headers = make_headers()
        params_dict = params.model_dump(exclude_none=True)

        return self.session.get(
            f"{self.url}:listVersions",
            headers=headers,
            params=params_dict,
            timeout=self.timeout,
        )

    def _call_rollback(self, request: RollbackRequest) -> requests.Response:
        headers = make_headers()
        data = request.model_dump_json(exclude_none=True)
        return self.session.post(
            f"{self.url}:rollback", headers=headers, data=data, timeout=self.timeout
        )

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
    etag = response.headers.get("etag", "")
    return RemoteConfig(template=template, etag=etag)


def make_headers(etag: Optional[str] = None) -> Dict:
    """Build request headers.

    Authorization and the ``x-goog-user-project`` quota-project header are
    added by the ``AuthorizedSession``; only content type and the optional
    ``If-Match`` etag precondition are set here.
    """
    headers = {
        "Content-Type": "application/json; UTF8",
    }

    if etag:
        headers["If-Match"] = etag

    return headers
