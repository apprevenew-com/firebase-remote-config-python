# Changelog

## 0.3.1 - 2026-09-23

- Fix `ConditionParser` rejecting numeric values equal to zero (`app.userProperty['x'] > 0`, `== 0`, `< 0.0`): the parsed value was tested for truthiness, so `0` was dropped and the condition failed validation.
- Fix `ConditionParser` failing on decimal values (`app.userProperty['x'] <= 3.99`); they now parse as `float`, while integers stay `int`.
- Fix timezone handling in parsed datetimes (`app.firstOpenTimestamp`, `dateTime`): a named zone such as `'Europe/Lisbon'` was attached with `datetime.replace`, giving the zone's historical LMT offset (a wrong instant), and was rendered back as `'LMT'`. Zones are now localized correctly, and conditions render the IANA zone name, so parsing and printing a condition returns the original expression.

## 0.3.0 - 2026-07-23

- Add an optional `seed` argument to `ConditionBuilder.PERCENT().GT()` / `.LTE()` / `.BETWEEN()`, so percent conditions can pin the hashing seed (renders as `percent('seed') <op> N`). Omitting it keeps the default per-project randomization.
- Validate `PercentCondition.seed` against Firebase's constraint (0-32 characters from `[-_.0-9a-zA-Z]`), so a malformed seed is rejected up front instead of by the Remote Config API.

## 0.2.0 - 2026-07-15

- Authenticate through google-auth's `AuthorizedSession`, so `RemoteConfigClient` now works with any Application Default Credentials — service account, workload identity, or `gcloud auth application-default login` — not just service accounts.
- Add `quota_project_id` constructor argument. User credentials without a quota project default it to `project_id`, which avoids the `403 SERVICE_DISABLED` the Remote Config API returns otherwise.
- Add `timeout` constructor argument (default 30s; `None` to disable). Requests were previously unbounded.
- Tolerate a missing `etag` response header instead of raising `KeyError`.
- Remove the unused `get_oauth_token` helper.
