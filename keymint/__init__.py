import requests
from .types import *
from ._version import __version__

__all__ = ['KeyMint', 'KeyMintApiError', '__version__']

class KeyMint:
    def __init__(self, api_key: str, base_url: str = "https://api.keymint.dev"):
        if not api_key:
            raise ValueError("API key is required to initialize the SDK.")
        
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def _handle_request(self, method: str, endpoint: str, params: dict = None, query_params: dict = None, idempotency_key: str = None):
        url = f'{self.base_url}{endpoint}'
        headers = self.headers.copy()
        if idempotency_key:
            headers['Idempotency-Key'] = idempotency_key
            
        try:
            if method.upper() == 'GET':
                response = requests.get(url, params=query_params, headers=headers)
            elif method.upper() == 'POST':
                response = requests.post(url, json=params, headers=headers)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=params, headers=headers)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, params=query_params, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
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

    def create_key(self, params: CreateKeyParams, idempotency_key: str = None) -> CreateKeyResponse:
        """
        Creates a new license key.
        :param params: Parameters for creating the key.
        :param idempotency_key: Optional unique identifier to ensure request idempotency.
        :returns: The created key information.
        """
        return self._handle_request('POST', '/key', params, idempotency_key=idempotency_key)

    def activate_key(self, params: ActivateKeyParams, idempotency_key: str = None) -> ActivateKeyResponse:
        """
        Activates a license key for a specific device.

        IMPORTANT: If `host_id` is omitted, Keymint generates a random Device ID for the request.
        Any subsequent activation attempt without a stable `host_id` will be treated as a brand-new 
        machine, consuming additional activation slots. Applications using anonymous activations 
        MUST cache the validation result locally.
        
        :param params: Activation parameters including productId, licenseKey, and optional hostId.
        :param idempotency_key: Optional unique identifier to ensure request idempotency.
        :return: Activation success message and licensee information.
        """
        return self._handle_request('POST', '/key/activate', params, idempotency_key=idempotency_key)

    def deactivate_key(self, params: DeactivateKeyParams, idempotency_key: str = None) -> DeactivateKeyResponse:
        """
        Deactivates a device from a license key.
        :param params: Parameters for deactivating the key.
        :param idempotency_key: Optional unique identifier to ensure request idempotency.
        :returns: The deactivation confirmation.
        """
        return self._handle_request('POST', '/key/deactivate', params, idempotency_key=idempotency_key)

    def floating_checkout(self, params: FloatingCheckoutParams, idempotency_key: str = None) -> FloatingCheckoutResponse:
        """
        Checks out a floating license seat.
        :param params: Parameters for checking out the license.
        :param idempotency_key: Optional unique identifier to ensure request idempotency.
        :returns: The checkout response containing sessionId and sessionSecret.
        """
        return self._handle_request('POST', '/key/checkout', params, idempotency_key=idempotency_key)

    def floating_heartbeat(self, params: FloatingHeartbeatParams, idempotency_key: str = None) -> FloatingHeartbeatResponse:
        """
        Sends a heartbeat to keep a floating license session alive.
        :param params: Parameters for the heartbeat (includes rotating signature).
        :param idempotency_key: Optional unique identifier to ensure request idempotency.
        :returns: The heartbeat response with extended expiry and new nonce.
        """
        return self._handle_request('POST', '/key/heartbeat', params, idempotency_key=idempotency_key)

    def floating_checkin(self, params: FloatingCheckinParams, idempotency_key: str = None) -> FloatingCheckinResponse:
        """
        Checks in a floating license session, releasing the seat.
        :param params: Parameters for checking in the license (includes rotating signature).
        :param idempotency_key: Optional unique identifier to ensure request idempotency.
        :returns: The checkin confirmation.
        """
        return self._handle_request('POST', '/key/checkin', params, idempotency_key=idempotency_key)

    def get_key(self, params: GetKeyParams) -> GetKeyResponse:
        """
        Retrieves detailed information about a specific license key.
        :param params: Parameters for fetching the key details.
        :returns: The license key details.
        """
        query_params = {
            'productId': params['productId'],
            'licenseKey': params['licenseKey']
        }
        return self._handle_request('GET', '/key', query_params=query_params)

    def block_key(self, params: BlockKeyParams, idempotency_key: str = None) -> BlockKeyResponse:
        """
        Blocks a specific license key.
        :param params: Parameters for blocking the key.
        :param idempotency_key: Optional unique identifier to ensure request idempotency.
        :returns: The block confirmation.
        """
        return self._handle_request('POST', '/key/block', params, idempotency_key=idempotency_key)

    def unblock_key(self, params: UnblockKeyParams, idempotency_key: str = None) -> UnblockKeyResponse:
        """
        Unblocks a previously blocked license key.
        :param params: Parameters for unblocking the key.
        :param idempotency_key: Optional unique identifier to ensure request idempotency.
        :returns: The unblock confirmation.
        """
        return self._handle_request('POST', '/key/unblock', params, idempotency_key=idempotency_key)

    # Customer Management Methods
    
    def create_customer(self, params: CreateCustomerParams, idempotency_key: str = None) -> CreateCustomerResponse:
        """
        Creates a new customer.
        :param params: Parameters for creating the customer.
        :param idempotency_key: Optional unique identifier to ensure request idempotency.
        :returns: The created customer information.
        """
        return self._handle_request('POST', '/customer', params, idempotency_key=idempotency_key)

    def get_all_customers(self, params: Optional[GetAllCustomersParams] = None) -> GetAllCustomersResponse:
        """
        Retrieves all customers associated with the authenticated user's account.
        :param params: Optional parameters for pagination and filtering (page, limit, email).
        :returns: List of all customers with pagination metadata.
        """
        return self._handle_request('GET', '/customer', query_params=params)

    def get_customer_by_id(self, params: GetCustomerByIdParams) -> GetCustomerByIdResponse:
        """
        Retrieves detailed information about a specific customer by their unique ID.
        :param params: Parameters containing the customer ID.
        :returns: The customer information.
        """
        query_params = {'customerId': params['customerId']}
        return self._handle_request('GET', '/customer/by-id', query_params=query_params)

    def update_customer(self, params: UpdateCustomerParams, idempotency_key: str = None) -> UpdateCustomerResponse:
        """
        Updates an existing customer's information.
        :param params: Parameters for updating the customer.
        :param idempotency_key: Optional unique identifier to ensure request idempotency.
        :returns: The update confirmation.
        """
        return self._handle_request('PUT', '/customer/by-id', params, idempotency_key=idempotency_key)

    def delete_customer(self, params: DeleteCustomerParams, idempotency_key: str = None) -> DeleteCustomerResponse:
        """
        Permanently deletes a customer and all associated license keys.
        :param params: Parameters containing the customer ID.
        :param idempotency_key: Optional unique identifier to ensure request idempotency.
        :returns: The deletion confirmation.
        """
        query_params = {'customerId': params['customerId']}
        return self._handle_request('DELETE', '/customer/by-id', query_params=query_params, idempotency_key=idempotency_key)

    def get_customer_with_keys(self, params: GetCustomerWithKeysParams) -> GetCustomerWithKeysResponse:
        """
        Retrieves detailed information about a customer along with their license keys.
        :param params: Parameters containing the customer ID.
        :returns: The customer information with associated license keys.
        """
        query_params = {'customerId': params['customerId']}
        return self._handle_request('GET', '/customer/keys', query_params=query_params)

    def toggle_customer_status(self, params: ToggleCustomerStatusParams, idempotency_key: str = None) -> ToggleCustomerStatusResponse:
        """
        Toggles the active status of a customer account (disable or enable).
        :param params: Parameters containing the customer ID.
        :param idempotency_key: Optional unique identifier to ensure request idempotency.
        :returns: The status toggle confirmation.
        """
        query_params = {'customerId': params['customerId']}
        return self._handle_request('POST', '/customer/disable', params=None, query_params=query_params, idempotency_key=idempotency_key)

    @staticmethod
    def verify_webhook_signature(payload: str, header: str, secret: str, tolerance_seconds: int = 300) -> bool:
        """
        Verifies a webhook payload signature received from Keymint.
        :param payload: The raw request body as a string.
        :param header: The value of the "Keymint-Signature" header.
        :param secret: The webhook endpoint's signing secret.
        :param tolerance_seconds: Time tolerance in seconds to prevent replay attacks. Defaults to 300 (5 minutes).
        :returns: True if the signature is valid, False otherwise.
        """
        import hmac
        import hashlib
        import time

        if not header or not secret:
            return False

        try:
            # Parse header (e.g. t=1719374021,v1=signature)
            timestamp_str = ""
            signature = ""
            parts = header.split(",")
            for part in parts:
                kv = part.strip().split("=", 1)
                if len(kv) == 2:
                    if kv[0] == "t":
                        timestamp_str = kv[1]
                    elif kv[0] == "v1":
                        signature = kv[1]

            if not timestamp_str or not signature:
                return False

            # Check timestamp validity
            try:
                timestamp_int = int(timestamp_str)
            except ValueError:
                return False

            now = int(time.time())
            if abs(now - timestamp_int) > tolerance_seconds:
                return False

            # Verify HMAC signature
            signable_content = f"{timestamp_str}.{payload}".encode("utf-8")
            expected_signature = hmac.new(
                secret.encode("utf-8"),
                signable_content,
                hashlib.sha256
            ).hexdigest()

            # Constant-time comparison to prevent timing attacks
            return hmac.compare_digest(expected_signature, signature)
        except Exception:
            return False


