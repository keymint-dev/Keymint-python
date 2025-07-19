# KeyMint Python SDK

Welcome to the official KeyMint SDK for Python! This library provides a simple and convenient way to interact with the KeyMint API, allowing you to manage license keys for your applications with ease.

## ✨ Features

*   **Simple & Intuitive**: A clean and modern API that is easy to learn and use.
*   **Type Hinting**: Uses Python's type hinting for a better developer experience.
*   **Comprehensive**: Covers all the essential KeyMint API endpoints.
*   **Well-Documented**: Clear and concise documentation with plenty of examples.
*   **Error Handling**: Standardized error handling to make debugging a breeze.

## 🚀 Quick Start

Here's a complete example of how to use the SDK to create and activate a license key:

```python
import os
from keymint import KeyMintSDK

def main():
    access_token = os.environ.get('KEYMINT_ACCESS_TOKEN')
    if not access_token:
        print('Please set the KEYMINT_ACCESS_TOKEN environment variable.')
        return

    sdk = KeyMintSDK(access_token)

    try:
        # 1. Create a new license key
        create_response = sdk.create_key({
            'productId': 'YOUR_PRODUCT_ID',
        })
        license_key = create_response['key']
        print(f'Key created: {license_key}')

        # 2. Activate the license key
        activate_response = sdk.activate_key({
            'productId': 'YOUR_PRODUCT_ID',
            'licenseKey': license_key,
            'hostId': 'UNIQUE_DEVICE_ID',
        })
        print(f"Key activated: {activate_response['message']}")
    except Exception as e:
        print(f'An error occurred: {e}')

if __name__ == '__main__':
    main()
```

## 📦 Installation

```bash
pip install keymint
```

## 🛠️ Usage

### Initialization

First, import the `KeyMintSDK` and initialize it with your access token. You can find your access token in your [KeyMint dashboard](https://keymint.dev/app/settings/api).

```python
from keymint import KeyMintSDK

access_token = 'YOUR_ACCESS_TOKEN'
sdk = KeyMintSDK(access_token)
```

### API Methods

All methods return a dictionary.

| Method          | Description                                     |
| --------------- | ----------------------------------------------- |
| `create_key`    | Creates a new license key.                      |
| `activate_key`  | Activates a license key for a device.           |
| `deactivate_key`| Deactivates a device from a license key.        |
| `get_key`       | Retrieves detailed information about a key.     |
| `block_key`     | Blocks a license key.                           |
| `unblock_key`   | Unblocks a previously blocked license key.      |

For more detailed information about the API methods and their parameters, please refer to the [API Reference](#api-reference) section below.

## 🚨 Error Handling

If an API call fails, the SDK will raise a `KeyMintApiError` exception. This object contains a `message`, `code`, and `status` attribute that you can use to handle the error.

```python
from keymint import KeyMintApiError

try:
    # ...
except KeyMintApiError as e:
    print(f'API Error: {e.message}')
    print(f'Status: {e.status}')
    print(f'Code: {e.code}')
except Exception as e:
    print(f'An unexpected error occurred: {e}')
```

## 📚 API Reference

### `KeyMintSDK(access_token, base_url)`

| Parameter      | Type     | Description                                                                 |
| -------------- | -------- | --------------------------------------------------------------------------- |
| `access_token` | `str`    | **Required.** Your KeyMint API access token.                                |
| `base_url`     | `str`    | *Optional.* The base URL for the KeyMint API. Defaults to `https://api.keymint.dev`. |

### `create_key(params)`

| Parameter        | Type     | Description                                                                 |
| ---------------- | -------- | --------------------------------------------------------------------------- |
| `productId`      | `str`    | **Required.** The ID of the product.                                        |
| `maxActivations` | `str`    | *Optional.* The maximum number of activations for the key.                  |
| `expiryDate`     | `str`    | *Optional.* The expiration date of the key in ISO 8601 format.              |
| `customerId`     | `str`    | *Optional.* The ID of an existing customer to associate with the key.       |
| `newCustomer`    | `dict`   | *Optional.* A dictionary containing the name and email of a new customer.   |

### `activate_key(params)`

| Parameter    | Type     | Description                                                                 |
| ------------ | -------- | --------------------------------------------------------------------------- |
| `productId`  | `str`    | **Required.** The ID of the product.                                        |
| `licenseKey` | `str`    | **Required.** The license key to activate.                                  |
| `hostId`     | `str`    | *Optional.* A unique identifier for the device.                             |
| `deviceTag`  | `str`    | *Optional.* A user-friendly name for the device.                            |

### `deactivate_key(params)`

| Parameter    | Type     | Description                                                                 |
| ------------ | -------- | --------------------------------------------------------------------------- |
| `productId`  | `str`    | **Required.** The ID of the product.                                        |
| `licenseKey` | `str`    | **Required.** The license key to deactivate.                                |
| `hostId`     | `str`    | *Optional.* The ID of the device to deactivate. If omitted, all devices are deactivated. |

### `get_key(params)`

| Parameter    | Type     | Description                                                                 |
| ------------ | -------- | --------------------------------------------------------------------------- |
| `productId`  | `str`    | **Required.** The ID of the product.                                        |
| `licenseKey` | `str`    | **Required.** The license key to retrieve.                                  |

### `block_key(params)`

| Parameter    | Type     | Description                                                                 |
| ------------ | -------- | --------------------------------------------------------------------------- |
| `productId`  | `str`    | **Required.** The ID of the product.                                        |
| `licenseKey` | `str`    | **Required.** The license key to block.                                     |

### `unblock_key(params)`

| Parameter    | Type     | Description                                                                 |
| ------------ | -------- | --------------------------------------------------------------------------- |
| `productId`  | `str`    | **Required.** The ID of the product.                                        |
| `licenseKey` | `str`    | **Required.** The license key to unblock.                                   |

## 📜 License

This SDK is licensed under the MIT License.
