# Changelog

## 2.7.0 - 2026-10-26

- Add `verify_offline_license`, which verifies a signed offline license (the `.lic` file from the dashboard or `sign_key`, or the bare token) locally against your Ed25519 public keys, with no network call. It checks the algorithm, key, signature, license type, product ID, machine code and expiry, returns an `OfflineLicense`, and raises `OfflineLicenseError` with a `code` (`malformed`, `unsupported_algorithm`, `unknown_key`, `bad_signature`, `wrong_type`, `wrong_product`, `wrong_machine`, `expired`) on failure.
- `product_id` is required: one signing key covers every product in an organization, so a verifier that skips the product check would let a license for one product unlock another.
- New required dependency: `cryptography>=41`, for Ed25519.
- CI now runs every test under `tests/`, including the shared offline-license test vectors.
- Add `delete_key` (`DELETE /key`), which permanently deletes a license key. Use `block_key` to stop a key reversibly.

## 2.6.0 - 2026-10-26

- Add `expirationDate` (ISO 8601 string, or `None` when the license never expires) to the `activate_key` and `floating_checkout` response types. On checkout it is separate from `expiresAt`, the seat lease. Additive; no other fields changed.
- Document reading the expiry, computing days left, and storing the last value in the README.

## 2.5.0 - 2026-09-09

- Synchronize licensing, floating-session, offline-signing, error, and customer contracts with the current API.
- Keep license credentials out of detailed-lookup URLs by using `x-license-key`.
- Add deterministic request and response contract tests.
- Correct the supported Python baseline to 3.10+, matching the syntax used by the package.
