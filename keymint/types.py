from typing import Any, Dict, List, Optional, TypedDict


class NewCustomer(TypedDict):
    name: str
    email: str | None

class KeyFormat(TypedDict):
    sections: int | None
    sectionLength: int | None
    separator: str | None
    charset: str | None
    prefix: str | None
    suffix: str | None
    case: str | None  # 'upper' | 'lower' | 'mixed'

class CreateKeyParams(TypedDict):
    productId: str
    maxActivations: str | None
    expiryDate: str | None
    customerId: str | None
    versionId: str | None
    metadata: dict[str, Any] | None
    newCustomer: NewCustomer | None
    allowedHosts: list[str] | None
    format: KeyFormat | None
    amountKeys: str | None
    licenseType: str | None  # 'node-locked' | 'floating'
    maxConcurrentSessions: int | None
    heartbeatInterval: int | None
    sessionLeaseDuration: int | None

class CreateKeyResponse(TypedDict):
    code: int
    key: str

class KeyMintApiError(Exception):
    def __init__(self, message: str, code: int, status: int | None = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status

class ActivateKeyParams(TypedDict):
    productId: str
    licenseKey: str
    hostId: str | None
    deviceTag: str | None
    licensee: dict[str, str] | None  # { name, email }
    version: str | None

class ActivateKeyResponse(TypedDict):
    code: int
    message: str
    licenseeName: str | None
    licenseeEmail: str | None
    metadata: dict[str, Any] | None
    versionId: str | None
    version: dict[str, Any] | None
    allowedHosts: list[str] | None

class DeactivateKeyParams(TypedDict):
    productId: str
    licenseKey: str
    hostId: str | None

class DeactivateKeyResponse(TypedDict):
    message: str
    code: int

class DeviceDetails(TypedDict):
    hostId: str
    deviceTag: str | None
    ipAddress: str | None
    activationTime: str

class LicenseDetails(TypedDict):
    id: str
    key: str
    productId: str
    maxActivations: int
    activations: int
    devices: list[DeviceDetails]
    activated: bool
    expirationDate: str | None
    versionId: str | None
    metadata: dict[str, Any] | None
    allowedHosts: list[str] | None
    version: dict[str, Any] | None

class CustomerDetails(TypedDict):
    id: str
    name: str | None
    email: str | None
    active: bool

class GetKeyParams(TypedDict):
    productId: str
    licenseKey: str

class GetKeyResponse(TypedDict):
    data: dict[str, Any]
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
    email: str | None

class CreateCustomerResponse(TypedDict):
    action: str
    status: bool
    message: str
    data: dict[str, Any]
    code: int

class GetAllCustomersParams(TypedDict):
    page: int | None
    limit: int | None
    email: str | None

class PaginationMeta(TypedDict):
    total: int
    page: int
    limit: int
    totalPages: int

class GetAllCustomersResponse(TypedDict):
    action: str
    status: bool
    data: list[dict[str, Any]]
    meta: PaginationMeta | None
    code: int

class GetCustomerByIdParams(TypedDict):
    customerId: str

class GetCustomerByIdResponse(TypedDict):
    action: str
    status: bool
    data: list[dict[str, Any]]
    code: int

class UpdateCustomerParams(TypedDict):
    customerId: str
    name: str | None  # Optional: Updated customer name
    email: str | None # Optional: Updated customer email

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
    expirationDate: str | None
    versionId: str | None
    metadata: dict[str, Any] | None
    allowedHosts: list[str] | None

class GetCustomerWithKeysParams(TypedDict):
    customerId: str

# GetCustomerWithKeys returns a flat LicenseKey[] — no wrapper object.
# Use List[Dict[str, Any]] for the response type.

class FloatingCheckoutParams(TypedDict):
    productId: str
    licenseKey: str
    hostId: str
    deviceTag: str | None
    userIdentifier: str | None
    apiKey: str | None

class FloatingCheckoutResponse(TypedDict):
    code: int
    message: str
    sessionId: str
    sessionSecret: str
    nextNonce: str
    expiresAt: str
    heartbeatInterval: int
    metadata: dict[str, Any] | None
    currentSessions: int | None
    maxSessions: int | None
    licenseeName: str | None
    licenseeEmail: str | None

class FloatingHeartbeatParams(TypedDict):
    productId: str
    licenseKey: str
    sessionId: str
    timestamp: Any  # rotating nonce (nextNonce) received from previous response
    signature: str
    apiKey: str | None

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
    apiKey: str | None

class FloatingCheckinResponse(TypedDict):
    code: int
    message: str

class UpdateKeyParams(TypedDict):
    productId: str
    licenseKey: str
    maxActivations: Any | None   # string or number
    expiryDate: str | None
    customerId: str | None
    newCustomer: NewCustomer | None
    metadata: dict[str, Any] | None
    versionId: str | None
    allowedHosts: list[str] | None
    licenseType: str | None  # 'node-locked' | 'floating'
    maxConcurrentSessions: int | None
    heartbeatInterval: int | None
    sessionLeaseDuration: int | None

class UpdateKeyResponse(TypedDict):
    code: int
    message: str
    affectedCount: int | None

class SignKeyParams(TypedDict):
    productId: str
    licenseKey: str
    hostId: str
    ttl: int | None

class SignKeyResponse(TypedDict):
    code: int
    file: dict[str, Any]  # { signedKey, keyId, publicKeyFingerprint }
