# Changelog

## 0.2.0 - 2026-07-15

- Authenticate through google-auth's `AuthorizedSession`, so `RemoteConfigClient` now works with any Application Default Credentials — service account, workload identity, or `gcloud auth application-default login` — not just service accounts.
- Add `quota_project_id` constructor argument. User credentials without a quota project default it to `project_id`, which avoids the `403 SERVICE_DISABLED` the Remote Config API returns otherwise.
- Add `timeout` constructor argument (default 30s; `None` to disable). Requests were previously unbounded.
- Tolerate a missing `etag` response header instead of raising `KeyError`.
- Remove the unused `get_oauth_token` helper.
