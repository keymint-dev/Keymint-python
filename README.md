# Keymint Python

A professional, production-ready SDK for integrating with the Keymint API in Python. Provides robust access to all major Keymint features, with type hints and modern error handling.

## Features
- **Type hints**: Full type hint support for better IDE integration and code safety.
- **Comprehensive**: Complete API coverage for all Keymint endpoints.
- **Consistent error handling**: All API errors are returned as structured objects or exceptions.
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
| `block_key`      | Blocks a license key.                           |
| `unblock_key`    | Unblocks a previously blocked license key.      |
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
| `delete_customer`       | Permanently deletes a customer and their keys.   |

### Webhook Verification

| Method                  | Description                                      |
|-------------------------|--------------------------------------------------|
| `verify_webhook_signature`| Verifies the signature of a webhook request payload. |

## License
MIT

## Support
For help, see [Keymint API docs](https://docs.keymint.dev) or open an issue.
