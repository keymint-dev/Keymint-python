# Keymint Python

A professional, production-ready SDK for integrating with the Keymint API in Python. Provides robust access to all major Keymint features, with type hints and modern error handling.

## Features
- **Type hints**: Full type hint support for better IDE integration and code safety.
- **Comprehensive**: Complete API coverage for all Keymint endpoints.
- **Consistent error handling**: All API errors are returned as structured objects or exceptions.
- **Offline licenses**: Verify signed `.lic` files locally with `verify_offline_license`.
- **Machine Identity**: Built-in utilities for hardware fingerprinting and stable installation IDs.

## Installation
Add the SDK to your project:

```bash
pip install keymint
```

## Usage

```python
import os
from keymint import KeyMint, identity

api_key = os.environ.get('KEYMINT_API_KEY')
product_id = os.environ.get('KEYMINT_PRODUCT_ID')

if not api_key or not product_id:
    raise ValueError('Please set the KEYMINT_API_KEY and KEYMINT_PRODUCT_ID environment variables.')

sdk = KeyMint(api_key)

# 1. Get a stable, unique ID for this machine
host_id = identity.get_or_create_installation_id()

# 2. Create a key authorized only for this machine
result = sdk.create_key({ 
    'productId': product_id,
    'allowedHosts': [host_id]
})

if result and 'key' in result:
    print(f"Created Key: {result['key']}")
```

## License Expiry

`activate_key` and `floating_checkout` return `expirationDate`: the license expiry as an ISO 8601 string (e.g. `"2027-03-01T00:00:00.000Z"`), or `None` when the license never expires. On `floating_checkout`, `expiresAt` is the seat lease, not the license expiry.

```python
from datetime import datetime, timezone
import math

result = sdk.activate_key({'productId': product_id, 'licenseKey': license_key, 'hostId': host_id})

expiration = result.get('expirationDate')
if expiration is None:
    print('License never expires')
else:
    expires_at = datetime.fromisoformat(expiration.replace('Z', '+00:00'))
    seconds_left = (expires_at - datetime.now(timezone.utc)).total_seconds()
    days_left = max(0, math.ceil(seconds_left / 86400))
    print(f'License expires {expires_at:%Y-%m-%d} ({days_left} days left)')

# Store the last value you received (e.g. in your app's settings file).
```

Store the last `expirationDate` you received. An expired license fails activation with the same generic invalid-key error as a wrong key, so the stored date is how your app can tell the user the license expired on that date instead of calling the key invalid.

## Offline Licenses

An offline license is a `.lic` file holding a token signed with your organization's Ed25519 key. Your app verifies it locally with `verify_offline_license`, with no network call.

1. **Get the `.lic` file** from the dashboard's Offline License dialog, or with `sign_key` from your own backend (it needs an admin API key, so never call it from the shipped app). The `hostId` you sign for becomes the license's machine code, so use the ID the customer's machine reports, e.g. `identity.get_or_create_installation_id()`.

   ```python
   # On your server, with host_id sent by the customer's machine:
   result = sdk.sign_key({'productId': product_id, 'licenseKey': license_key, 'hostId': host_id})
   lic = result['file']  # the .lic contents; deliver this to the customer
   ```

2. **Bundle your public key** with the app: copy the PEM from **Developer → Public Keys** in the dashboard. It is a public key, so shipping it is safe.

3. **Verify** with the product ID and this machine's code:

   ```python
   from keymint import OfflineLicenseError, identity, verify_offline_license

   PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
   MCowBQYDK2VwAyEA...
   -----END PUBLIC KEY-----
   """

   with open('license.lic', encoding='utf-8') as f:
       lic = f.read()

   try:
       offline = verify_offline_license(
           lic,
           public_keys=[PUBLIC_KEY],
           product_id='prod_...',  # this app's product ID
           machine_code=identity.get_or_create_installation_id(),
       )
       print(f'Licensed until {offline.expires_at:%Y-%m-%d}')
   except OfflineLicenseError as err:
       if err.code == 'expired':
           ...  # ask the customer to renew or reconnect
       elif err.code in ('wrong_product', 'wrong_machine'):
           ...  # a real license, but not for this product or this machine
       else:
           ...  # malformed, unsupported_algorithm, unknown_key, bad_signature, wrong_type: not a valid license
   ```

`verify_offline_license` accepts the `.lic` file contents or the bare token and returns an `OfflineLicense` with `license_key`, `product_id`, `machine_code`, `key_id`, `issued_at` (or `None`) and `expires_at` (timezone-aware UTC datetimes). On failure it raises `OfflineLicenseError`; `err.code` is one of:

| Code | Meaning |
|---|---|
| `malformed` | Not a license file or token, or required claims (`exp`, `sub`) are missing or invalid. |
| `unsupported_algorithm` | The token is not signed with EdDSA (e.g. `none`, `HS256`). |
| `unknown_key` | Signed by a key that isn't in `public_keys`. |
| `bad_signature` | The signature doesn't match: the file was altered or forged. |
| `wrong_type` | The token is not an offline license. |
| `wrong_product` | The license is for a different product. |
| `wrong_machine` | The license is for a different machine. |
| `expired` | Past its expiry, plus `clock_skew` (default 60 seconds, max 3600). |

Bad arguments (no public keys, a PEM that isn't an Ed25519 public key, an empty `product_id` or `machine_code`, `clock_skew` outside 0..3600, a naive `now`) raise `ValueError` or `TypeError`, not `OfflineLicenseError`.

**`product_id` is required.** One signing key covers all of an organization's products, so without the product check a license for a cheap product would unlock an expensive one.

**Clock rollback.** The SDK can't tell if the system clock was set back. To guard against it, store the latest time you have trusted (for example, after each successful run) and pass the later of the two as `now`. `now` must be timezone-aware:

```python
from datetime import datetime, timezone

now = max(datetime.now(timezone.utc), last_trusted_time)
offline = verify_offline_license(lic, public_keys=[PUBLIC_KEY], product_id=product_id,
                                 machine_code=machine_code, now=now)
```

`public_keys` accepts several keys, so apps are ready for key rotation. An offline license stays valid until it expires; it can't be revoked before then.

Offline verification uses the [`cryptography`](https://pypi.org/project/cryptography/) package, which `pip install keymint` installs (`cryptography>=41`).

## Machine Identity
Keymint provides utilities to uniquely identify machines for node-locking:

- `identity.get_or_create_installation_id()`: **Recommended.** Generates a stable UUID anchored to hardware and persists it to `~/.keymint/installation-id`.
- `identity.get_machine_id()`: Generates a SHA-256 fingerprint based on BIOS UUID, OS machine ID, and MAC address.

## API Methods

### License Key Management

| Method           | Description                                     |
|------------------|-------------------------------------------------|
| `create_key`     | Creates a new license key.                      |
| `activate_key`   | Activates a license key for a device.           |
| `deactivate_key` | Deactivates a device from a license key.        |
| `get_key`        | Retrieves detailed information about a key.     |
| `update_key`     | Updates an existing license key.                |
| `block_key`      | Blocks a license key.                           |
| `unblock_key`    | Unblocks a previously blocked license key.      |
| `delete_key`     | Permanently deletes a license key.              |
| `sign_key`       | Signs a key for offline validation using an admin API key.|
| `floating_checkout` | Checks out a floating license seat.          |
| `floating_heartbeat`| Sends a heartbeat to keep a session alive.   |
| `floating_checkin`  | Checks in a session, releasing the seat.     |

### Customer Management

| Method                  | Description                                      |
|-------------------------|--------------------------------------------------|
| `create_customer`       | Creates a new customer.                          |
| `get_all_customers`     | Retrieves all customers.                         |
| `get_customer_by_id`    | Gets a specific customer by ID.                  |
| `get_customer_with_keys`| Gets a customer along with their license keys.   |
| `update_customer`       | Updates customer information.                    |
| `toggle_customer_status`| Toggles customer active status.                  |
| `delete_customer`       | Deletes a customer. Their license keys are kept; use `delete_key` to remove them. |

### Webhook Verification

| Method                  | Description                                      |
|-------------------------|--------------------------------------------------|
| `verify_webhook_signature`| Verifies the signature of a webhook request payload. |

## Idempotency

All mutating SDK methods support idempotency keys to safely retry requests in case of network drops. Pass a unique string (recommended: UUID v4) as the optional `idempotency_key` keyword argument:

```python
result = sdk.create_key({ 
    'productId': product_id,
}, idempotency_key='9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d')
```

## License
MIT

## Support
For help, see [Keymint API docs](https://docs.keymint.dev) or open an issue.
