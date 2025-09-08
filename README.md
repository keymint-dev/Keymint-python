# KeyMint Python SDK

A professional, production-ready SDK for integrating with the KeyMint API in Python. Provides robust access to all major KeyMint features, with type hints and modern error handling.

## Features
- **Type hints**: Full type hint support for better IDE integration and code safety.
- **Comprehensive**: Complete API coverage for all KeyMint endpoints.
- **Consistent error handling**: All API errors are returned as structured objects or exceptions.
- **Security**: Credentials are always loaded from environment variables.

## Installation
Add the SDK to your project:

```bash
pip install keymint
```

## Usage

```python
import os
import keymint

access_token = os.environ.get('KEYMINT_ACCESS_TOKEN')
product_id = os.environ.get('KEYMINT_PRODUCT_ID')

if not access_token or not product_id:
    raise ValueError('Please set the KEYMINT_ACCESS_TOKEN and KEYMINT_PRODUCT_ID environment variables.')

sdk = keymint.KeyMint(access_token)

# Example: Create a key
result = sdk.create_key({ 'productId': product_id })
if result and 'key' in result:
    key = result['key']
    # ...
else:
    # Handle error
    pass
```

## Error Handling
All SDK methods return a dictionary. If an API call fails, the SDK raises a `KeyMintApiError` exception with `message`, `code`, and `status` attributes.

## API Methods

All methods return a dictionary.

### License Key Management

| Method           | Description                                     |
|------------------|-------------------------------------------------|
| `create_key`     | Creates a new license key.                      |
| `activate_key`   | Activates a license key for a device.           |
| `deactivate_key` | Deactivates a device from a license key.        |
| `get_key`        | Retrieves detailed information about a key.     |
| `block_key`      | Blocks a license key.                           |
| `unblock_key`    | Unblocks a previously blocked license key.      |

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

For detailed parameter and response types, see the [KeyMint API docs](https://docs.keymint.dev) or use your IDE's autocomplete.

## License
MIT

## Support
For help, see [KeyMint API docs](https://docs.keymint.dev) or open an issue.
