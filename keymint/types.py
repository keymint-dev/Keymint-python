from typing import TypedDict, Optional, List, Dict, Any

class NewCustomer(TypedDict):
    name: str
    email: Optional[str]

class CreateKeyParams(TypedDict):
    productId: str
    maxActivations: Optional[str]
    expiryDate: Optional[str]
    customerId: Optional[str]
    newCustomer: Optional[NewCustomer]

class CreateKeyResponse(TypedDict):
    code: int
    key: str

class KeyMintApiError(Exception):
    def __init__(self, message: str, code: int, status: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status

class ActivateKeyParams(TypedDict):
    productId: str
    licenseKey: str
    hostId: Optional[str]
    deviceTag: Optional[str]

class ActivateKeyResponse(TypedDict):
    code: int
    message: str
    licensee_name: Optional[str]
    licensee_email: Optional[str]

class DeactivateKeyParams(TypedDict):
    productId: str
    licenseKey: str
    hostId: Optional[str]

class DeactivateKeyResponse(TypedDict):
    message: str
    code: int

class DeviceDetails(TypedDict):
    host_id: str
    device_tag: Optional[str]
    ip_address: Optional[str]
    activation_time: str

class LicenseDetails(TypedDict):
    id: str
    key: str
    product_id: str
    max_activations: int
    activations: int
    devices: List[DeviceDetails]
    activated: bool
    expiration_date: Optional[str]

class CustomerDetails(TypedDict):
    id: str
    name: Optional[str]
    email: Optional[str]
    active: bool

class GetKeyParams(TypedDict):
    productId: str
    licenseKey: str

class GetKeyResponse(TypedDict):
    code: int
    data: Dict[str, Any]

class BlockKeyParams(TypedDict):
    productId: str
    licenseKey: str

class BlockKeyResponse(TypedDict):
    message: str
    code: int

class UnblockKeyParams(TypedDict):
    productId: str
    licenseKey: str

class UnblockKeyResponse(TypedDict):
    message: str
    code: int
