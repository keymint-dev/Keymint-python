import unittest
from unittest.mock import patch, MagicMock
import requests
from keymint import KeyMintSDK, KeyMintApiError
from keymint.types import *

class TestKeyMintSDK(unittest.TestCase):

    def setUp(self):
        self.sdk = KeyMintSDK(access_token="test_token")

    @patch('requests.post')
    def test_create_key_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {'code': 0, 'key': 'test_key'}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        params: CreateKeyParams = {'productId': 'prod_123'}
        response = self.sdk.create_key(params)

        self.assertEqual(response['key'], 'test_key')
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_create_key_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {'message': 'Error', 'code': 1}
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_post.return_value = mock_response

        params: CreateKeyParams = {'productId': 'prod_123'}
        with self.assertRaises(KeyMintApiError) as context:
            self.sdk.create_key(params)
        
        self.assertEqual(context.exception.code, 1)

    @patch('requests.post')
    def test_activate_key_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {'code': 0, 'message': 'activated'}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        params: ActivateKeyParams = {'productId': 'prod_123', 'licenseKey': 'key_123'}
        response = self.sdk.activate_key(params)

        self.assertEqual(response['message'], 'activated')
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_deactivate_key_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {'code': 0, 'message': 'deactivated'}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        params: DeactivateKeyParams = {'productId': 'prod_123', 'licenseKey': 'key_123'}
        response = self.sdk.deactivate_key(params)

        self.assertEqual(response['message'], 'deactivated')
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_get_key_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {'code': 0, 'data': {'license': {}}}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        params: GetKeyParams = {'productId': 'prod_123', 'licenseKey': 'key_123'}
        response = self.sdk.get_key(params)

        self.assertIn('license', response['data'])
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_block_key_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {'code': 0, 'message': 'blocked'}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        params: BlockKeyParams = {'productId': 'prod_123', 'licenseKey': 'key_123'}
        response = self.sdk.block_key(params)

        self.assertEqual(response['message'], 'blocked')
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_unblock_key_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {'code': 0, 'message': 'unblocked'}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        params: UnblockKeyParams = {'productId': 'prod_123', 'licenseKey': 'key_123'}
        response = self.sdk.unblock_key(params)

        self.assertEqual(response['message'], 'unblocked')
        mock_post.assert_called_once()

if __name__ == '__main__':
    unittest.main()
