from unittest.mock import Mock, patch

import pytest
import requests

from keymint import KeyMint, KeyMintApiError


def response(payload, status=200):
    result = Mock()
    result.json.return_value = payload
    result.status_code = status
    if status >= 400:
        error = requests.exceptions.HTTPError()
        error.response = result
        result.raise_for_status.side_effect = error
    return result


@patch("keymint.requests.get")
def test_get_key_uses_header_not_query(mock_get):
    mock_get.return_value = response({"code": 0, "data": {"license": {"productId": "product 123"}}})

    KeyMint("readonly_test").get_key({"productId": "product 123", "licenseKey": "secret/license+key"})

    _, kwargs = mock_get.call_args
    assert kwargs["params"] == {"productId": "product 123"}
    assert kwargs["headers"]["x-license-key"] == "secret/license+key"
    assert "licenseKey" not in kwargs["params"]


@patch("keymint.requests.post")
def test_sign_key_returns_serialized_file(mock_post):
    mock_post.return_value = response({"file": '{"signedKey":"signature","keyId":"key_123"}'})

    result = KeyMint("admin_test").sign_key({
        "productId": "product_123", "licenseKey": "license_123", "hostId": "host_123"
    })

    assert isinstance(result["file"], str)


@patch("keymint.requests.post")
def test_nested_error_preserves_server_message(mock_post):
    mock_post.return_value = response({
        "success": False,
        "error": {"code": "CUSTOMER_EMAIL_EXISTS", "message": "Customer email already exists in team"},
        "code": 1,
    }, 409)

    with pytest.raises(KeyMintApiError, match="Customer email already exists in team"):
        KeyMint("admin_test").create_key({"productId": "product_123"})
