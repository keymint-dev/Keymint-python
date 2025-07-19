import requests
from .types import *

class KeyMintSDK:
    def __init__(self, access_token: str, base_url: str = "https://api.keymint.dev"):
        if not access_token:
            raise ValueError("Access token is required to initialize the SDK.")
        
        self.access_token = access_token
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

    def _handle_request(self, endpoint: str, params: dict):
        url = f'{self.base_url}{endpoint}'
        try:
            response = requests.post(url, json=params, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            try:
                error_data = http_err.response.json()
                raise KeyMintApiError(
                    message=error_data.get('message', 'An API error occurred'),
                    code=error_data.get('code', -1),
                    status=http_err.response.status_code
                )
            except ValueError:
                raise KeyMintApiError(
                    message=str(http_err),
                    code=-1,
                    status=http_err.response.status_code
                )
        except Exception as err:
            raise KeyMintApiError(message=str(err), code=-1)

    def create_key(self, params: CreateKeyParams) -> CreateKeyResponse:
        """
        Creates a new license key.
        :param params: Parameters for creating the key.
        :returns: The created key information.
        """
        return self._handle_request('/create-key', params)

    def activate_key(self, params: ActivateKeyParams) -> ActivateKeyResponse:
        """
        Activates a license key for a specific device.
        :param params: Parameters for activating the key.
        :returns: The activation status.
        """
        return self._handle_request('/activate-key', params)

    def deactivate_key(self, params: DeactivateKeyParams) -> DeactivateKeyResponse:
        """
        Deactivates a device from a license key.
        :param params: Parameters for deactivating the key.
        :returns: The deactivation confirmation.
        """
        return self._handle_request('/deactivate-key', params)

    def get_key(self, params: GetKeyParams) -> GetKeyResponse:
        """
        Retrieves detailed information about a specific license key.
        :param params: Parameters for fetching the key details.
        :returns: The license key details.
        """
        return self._handle_request('/get-key', params)

    def block_key(self, params: BlockKeyParams) -> BlockKeyResponse:
        """
        Blocks a specific license key.
        :param params: Parameters for blocking the key.
        :returns: The block confirmation.
        """
        return self._handle_request('/block-key', params)

    def unblock_key(self, params: UnblockKeyParams) -> UnblockKeyResponse:
        """
        Unblocks a previously blocked license key.
        :param params: Parameters for unblocking the key.
        :returns: The unblock confirmation.
        """
        return self._handle_request('/unblock-key', params)
