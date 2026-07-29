from typing import TypedDict, Optional, List, Dict, Any

class NewCustomer(TypedDict):
    name: str
    email: Optional[str]

class KeyFormat(TypedDict):
    sections: Optional[int]
    sectionLength: Optional[int]
    separator: Optional[str]
    charset: Optional[str]
    prefix: Optional[str]
    suffix: Optional[str]
    case: Optional[str]  # 'upper' | 'lower' | 'mixed'

class CreateKeyParams(TypedDict):
    productId: str
    maxActivations: Optional[str]
    expiryDate: Optional[str]
    customerId: Optional[str]
    versionId: Optional[str]
    metadata: Optional[Dict[str, Any]]
    newCustomer: Optional[NewCustomer]
    allowedHosts: Optional[List[str]]
    format: Optional[KeyFormat]
    amountKeys: Optional[str]
    licenseType: Optional[str]  # 'node-locked' | 'floating'
    maxConcurrentSessions: Optional[int]
    heartbeatInterval: Optional[int]
    sessionLeaseDuration: Optional[int]

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
    licensee: Optional[Dict[str, str]]  # { name, email }
    version: Optional[str]

class ActivateKeyResponse(TypedDict):
    code: int
    message: str
    licenseeName: Optional[str]
    licenseeEmail: Optional[str]
    metadata: Optional[Dict[str, Any]]
    versionId: Optional[str]
    version: Optional[Dict[str, Any]]
    allowedHosts: Optional[List[str]]

class DeactivateKeyParams(TypedDict):
    productId: str
    licenseKey: str
    hostId: Optional[str]

class DeactivateKeyResponse(TypedDict):
    message: str
    code: int

class DeviceDetails(TypedDict):
    hostId: str
    deviceTag: Optional[str]
    ipAddress: Optional[str]
    activationTime: str

class LicenseDetails(TypedDict):
    id: str
    key: str
    productId: str
    maxActivations: int
    activations: int
    devices: List[DeviceDetails]
    activated: bool
    expirationDate: Optional[str]
    versionId: Optional[str]
    metadata: Optional[Dict[str, Any]]
    allowedHosts: Optional[List[str]]
    version: Optional[Dict[str, Any]]

class CustomerDetails(TypedDict):
    id: str
    name: Optional[str]
    email: Optional[str]
    active: bool

class GetKeyParams(TypedDict):
    productId: str
    licenseKey: str

class GetKeyResponse(TypedDict):
    data: Dict[str, Any]
    code: int

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

# Customer Management Types

class CreateCustomerParams(TypedDict):
    name: str
    email: Optional[str]

class CreateCustomerResponse(TypedDict):
    action: str
    status: bool
    message: str
    data: Dict[str, Any]
    code: int

class GetAllCustomersParams(TypedDict):
    page: Optional[int]
    limit: Optional[int]
    email: Optional[str]

class PaginationMeta(TypedDict):
    total: int
    page: int
    limit: int
    totalPages: int

class GetAllCustomersResponse(TypedDict):
    action: str
    status: bool
    data: List[Dict[str, Any]]
    meta: Optional[PaginationMeta]
    code: int

class GetCustomerByIdParams(TypedDict):
    customerId: str

class GetCustomerByIdResponse(TypedDict):
    action: str
    status: bool
    data: List[Dict[str, Any]]
    code: int

class UpdateCustomerParams(TypedDict):
    customerId: str
    name: Optional[str]  # Optional: Updated customer name
    email: Optional[str] # Optional: Updated customer email

class UpdateCustomerResponse(TypedDict):
    action: str
    status: bool
    code: int

class DeleteCustomerParams(TypedDict):
    customerId: str

class DeleteCustomerResponse(TypedDict):
    action: str
    status: bool
    code: int

class ToggleCustomerStatusParams(TypedDict):
    customerId: str

class ToggleCustomerStatusResponse(TypedDict):
    action: str
    status: bool
    message: str
    code: int

class CustomerLicenseKey(TypedDict):
    id: str
    key: str
    productId: str
    maxActivations: int
    activations: int
    activated: bool
    expirationDate: Optional[str]
    versionId: Optional[str]
    metadata: Optional[Dict[str, Any]]
    allowedHosts: Optional[List[str]]

class GetCustomerWithKeysParams(TypedDict):
    customerId: str

# GetCustomerWithKeys returns a flat LicenseKey[] — no wrapper object.
# Use List[Dict[str, Any]] for the response type.

class FloatingCheckoutParams(TypedDict):
    productId: str
    licenseKey: str
    hostId: str
    deviceTag: Optional[str]
    userIdentifier: Optional[str]
    apiKey: Optional[str]

class FloatingCheckoutResponse(TypedDict):
    code: int
    message: str
    sessionId: str
    sessionSecret: str
    nextNonce: str
    expiresAt: str
    heartbeatInterval: int
    metadata: Optional[Dict[str, Any]]
    currentSessions: Optional[int]
    maxSessions: Optional[int]
    licenseeName: Optional[str]
    licenseeEmail: Optional[str]

class FloatingHeartbeatParams(TypedDict):
    productId: str
    licenseKey: str
    sessionId: str
    timestamp: Any  # rotating nonce (nextNonce) received from previous response
    signature: str
    apiKey: Optional[str]

class FloatingHeartbeatResponse(TypedDict):
    code: int
    message: str
    expiresAt: str
    nextNonce: str

class FloatingCheckinParams(TypedDict):
    productId: str
    licenseKey: str
    sessionId: str
    timestamp: Any  # rotating nonce (nextNonce) received from previous response
    signature: str
    apiKey: Optional[str]

class FloatingCheckinResponse(TypedDict):
    code: int
    message: str

class UpdateKeyParams(TypedDict):
    productId: str
    licenseKey: str
    maxActivations: Optional[Any]   # string or number
    expiryDate: Optional[str]
    customerId: Optional[str]
    newCustomer: Optional[NewCustomer]
    metadata: Optional[Dict[str, Any]]
    versionId: Optional[str]
    allowedHosts: Optional[List[str]]
    licenseType: Optional[str]  # 'node-locked' | 'floating'
    maxConcurrentSessions: Optional[int]
    heartbeatInterval: Optional[int]
    sessionLeaseDuration: Optional[int]

class UpdateKeyResponse(TypedDict):
    code: int
    message: str
    affectedCount: Optional[int]

class SignKeyParams(TypedDict):
    productId: str
    licenseKey: str
    hostId: str
    ttl: Optional[int]

class SignKeyResponse(TypedDict):
    code: int
    file: Dict[str, Any]  # { signedKey, keyId, publicKeyFingerprint }
