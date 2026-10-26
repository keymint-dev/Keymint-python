# Changelog

## Unreleased

- Add `expirationDate` (ISO 8601 string, or `None` when the license never expires) to the `activate_key` and `floating_checkout` response types. On checkout it is separate from `expiresAt`, the seat lease. Additive; no other fields changed.
- Document reading the expiry, computing days left, and storing the last value in the README.

## 2.5.0 - 2026-09-09

- Synchronize licensing, floating-session, offline-signing, error, and customer contracts with the current API.
- Keep license credentials out of detailed-lookup URLs by using `x-license-key`.
- Add deterministic request and response contract tests.
- Correct the supported Python baseline to 3.10+, matching the syntax used by the package.
