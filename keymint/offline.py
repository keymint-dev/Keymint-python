"""
Offline license verification for the Keymint Python SDK.

Verifies a signed offline license (the ``.lic`` file from the dashboard or
``KeyMint.sign_key``) locally, with no network call. The license is an Ed25519
JWT signed by your organization's key; you bundle the public key PEM from
Developer -> Public Keys with your app.

One signing key covers every product in an organization, so the product ID is
a required argument: without it a license for one product would unlock another.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import math
import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

from cryptography.exceptions import InvalidSignature, UnsupportedAlgorithm
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    load_pem_public_key,
)

__all__ = [
    'OfflineLicense',
    'OfflineLicenseError',
    'OfflineLicenseErrorCode',
    'verify_offline_license',
]

DEFAULT_CLOCK_SKEW = 60
MAX_CLOCK_SKEW = 3600

# fullmatch, not match: '$' would also accept a trailing newline.
_SEGMENT = re.compile(r'[A-Za-z0-9_-]*')
# The characters JavaScript's String.prototype.trim removes, so every SDK
# accepts the same inputs as the reference implementation.
_WHITESPACE = (
    ' \t\n\v\f\r         '
    '        　﻿'
)
_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


class OfflineLicenseErrorCode(str, Enum):
    """Why an offline license was rejected. Compares equal to its string value."""

    MALFORMED = 'malformed'
    UNSUPPORTED_ALGORITHM = 'unsupported_algorithm'
    UNKNOWN_KEY = 'unknown_key'
    BAD_SIGNATURE = 'bad_signature'
    WRONG_TYPE = 'wrong_type'
    WRONG_PRODUCT = 'wrong_product'
    WRONG_MACHINE = 'wrong_machine'
    EXPIRED = 'expired'

    def __str__(self) -> str:
        return self.value


_MESSAGES = {
    OfflineLicenseErrorCode.MALFORMED: 'The offline license is not a valid license file or token.',
    OfflineLicenseErrorCode.UNSUPPORTED_ALGORITHM: 'The offline license uses an unsupported signing algorithm.',
    OfflineLicenseErrorCode.UNKNOWN_KEY: 'The offline license was not signed by a trusted public key.',
    OfflineLicenseErrorCode.BAD_SIGNATURE: 'The offline license signature is invalid.',
    OfflineLicenseErrorCode.WRONG_TYPE: 'The token is not an offline license.',
    OfflineLicenseErrorCode.WRONG_PRODUCT: 'The offline license is for a different product.',
    OfflineLicenseErrorCode.WRONG_MACHINE: 'The offline license is for a different machine.',
    OfflineLicenseErrorCode.EXPIRED: 'The offline license has expired.',
}


class OfflineLicenseError(Exception):
    """
    Raised when an offline license fails verification.

    ``code`` is an :class:`OfflineLicenseErrorCode` (a ``str``), e.g. ``"expired"``.
    The message never contains the license key.
    """

    def __init__(self, code: OfflineLicenseErrorCode, message: str | None = None):
        self.code = code
        self.message = message or _MESSAGES[code]
        super().__init__(self.message)


@dataclass(frozen=True)
class OfflineLicense:
    """A verified offline license. Times are timezone-aware UTC datetimes."""

    license_key: str = field(repr=False)
    product_id: str
    machine_code: str
    key_id: str
    issued_at: datetime | None
    expires_at: datetime


def _key_id(key: Ed25519PublicKey) -> str:
    """base64url (no padding) of SHA-256 over the key's SPKI DER, as the server computes it."""
    der = key.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
    return base64.urlsafe_b64encode(hashlib.sha256(der).digest()).rstrip(b'=').decode('ascii')


def _load_public_key(pem: str, index: int) -> Ed25519PublicKey:
    if not isinstance(pem, str):
        raise TypeError(f'public_keys[{index}] must be a PEM string')
    try:
        key = load_pem_public_key(pem.encode('utf-8'))
    except (ValueError, TypeError, UnsupportedAlgorithm) as err:
        raise ValueError(f'public_keys[{index}] is not a valid PEM public key') from err
    if not isinstance(key, Ed25519PublicKey):
        # A valid PEM of the wrong key type is a bad value, not a bad type (spec).
        raise ValueError(f'public_keys[{index}] is not an Ed25519 public key')  # noqa: TRY004
    return key


def _b64url_decode(segment: str) -> bytes | None:
    try:
        return base64.urlsafe_b64decode(segment + '=' * (-len(segment) % 4))
    except (binascii.Error, ValueError):
        return None


def _reject_constant(name: str) -> Any:
    # JSON has no NaN or Infinity; Python's json module accepts them by default.
    raise ValueError(f'invalid JSON constant {name}')


def _parse_json(text: str) -> Any:
    """json.loads, raising ValueError for anything JSON.parse would reject."""
    try:
        return json.loads(text, parse_constant=_reject_constant)
    except RecursionError as err:  # deeply nested input
        raise ValueError('JSON nested too deeply') from err


def _decode_json_object(segment: str) -> dict[str, Any] | None:
    raw = _b64url_decode(segment)
    if raw is None:
        return None
    try:
        value = _parse_json(raw.decode('utf-8', errors='replace'))
    except ValueError:
        return None
    return value if isinstance(value, dict) else None


def _is_number(value: Any) -> bool:
    # bool is a subclass of int in Python; JSON true/false are not numbers.
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _to_datetime(seconds: float) -> datetime | None:
    try:
        if not math.isfinite(seconds):
            return None
        return _EPOCH + timedelta(seconds=seconds)
    except (OverflowError, ValueError):
        return None


def verify_offline_license(
    license: str,
    *,
    public_keys: Sequence[str],
    product_id: str,
    machine_code: str,
    now: datetime | None = None,
    clock_skew: float = DEFAULT_CLOCK_SKEW,
) -> OfflineLicense:
    """
    Verifies an offline license locally and returns its claims.

    :param license: The ``.lic`` file contents (JSON string) or the bare signed token.
    :param public_keys: One or more trusted Ed25519 public keys (SPKI PEM strings)
        from Developer -> Public Keys.
    :param product_id: The product this app is. Must equal the license's product.
    :param machine_code: This machine's code. Must equal the license's machine code.
    :param now: The time to check expiry against. Must be timezone-aware; naive
        datetimes are rejected. Defaults to the system clock. To guard against
        clock rollback, pass ``max(system time, last trusted time)``.
    :param clock_skew: Seconds of leeway on expiry, 0 to 3600. Defaults to 60.
    :returns: The verified :class:`OfflineLicense`.
    :raises OfflineLicenseError: The license failed verification; see ``.code``.
    :raises ValueError: An argument is invalid (no keys, a key that is not an
        Ed25519 public key PEM, an empty product or machine code, a naive ``now``,
        or ``clock_skew`` out of range).
    :raises TypeError: An argument has the wrong type.
    """
    if not isinstance(license, str):
        raise TypeError('license must be a string')
    if isinstance(public_keys, (str, bytes)):
        raise TypeError('public_keys must be a sequence of PEM strings, not a single string')
    public_keys = list(public_keys)
    if not public_keys:
        raise ValueError('public_keys must contain at least one key')
    if not isinstance(product_id, str):
        raise TypeError('product_id must be a string')
    if not product_id:
        raise ValueError('product_id is required')
    if not isinstance(machine_code, str):
        raise TypeError('machine_code must be a string')
    if not machine_code:
        raise ValueError('machine_code is required')
    if not _is_number(clock_skew):
        raise TypeError('clock_skew must be a number of seconds')
    if not 0 <= clock_skew <= MAX_CLOCK_SKEW:
        raise ValueError(f'clock_skew must be between 0 and {MAX_CLOCK_SKEW} seconds')
    if now is None:
        now = datetime.now(timezone.utc)
    elif not isinstance(now, datetime):
        raise TypeError('now must be a datetime')
    elif now.tzinfo is None or now.utcoffset() is None:
        raise ValueError('now must be timezone-aware, e.g. datetime.now(timezone.utc)')

    keys: dict[str, Ed25519PublicKey] = {}
    for index, pem in enumerate(public_keys):
        key = _load_public_key(pem, index)
        keys[_key_id(key)] = key

    # 1. Parse: a .lic file (JSON) or a bare token.
    token = license.strip(_WHITESPACE)
    if token.startswith('{'):
        try:
            file = _parse_json(token)
        except ValueError:
            raise OfflineLicenseError(OfflineLicenseErrorCode.MALFORMED) from None
        if not isinstance(file, dict) or not isinstance(file.get('signedKey'), str):
            raise OfflineLicenseError(OfflineLicenseErrorCode.MALFORMED)
        token = file['signedKey']
    parts = token.split('.')
    if len(parts) != 3 or not all(_SEGMENT.fullmatch(part) for part in parts):
        raise OfflineLicenseError(OfflineLicenseErrorCode.MALFORMED)
    header_b64, payload_b64, signature_b64 = parts
    header = _decode_json_object(header_b64)
    payload = _decode_json_object(payload_b64)
    if header is None or payload is None:
        raise OfflineLicenseError(OfflineLicenseErrorCode.MALFORMED)

    # 2. Algorithm: exactly EdDSA, no critical extensions.
    if header.get('alg') != 'EdDSA' or 'crit' in header:
        raise OfflineLicenseError(OfflineLicenseErrorCode.UNSUPPORTED_ALGORITHM)

    # 3. Key: the kid must name a trusted key.
    kid = header.get('kid')
    key = keys.get(kid) if isinstance(kid, str) else None
    if key is None:
        raise OfflineLicenseError(OfflineLicenseErrorCode.UNKNOWN_KEY)

    # 4. Signature over the segments exactly as received.
    signature = _b64url_decode(signature_b64)
    if signature is None or len(signature) != 64:
        raise OfflineLicenseError(OfflineLicenseErrorCode.BAD_SIGNATURE)
    try:
        key.verify(signature, f'{header_b64}.{payload_b64}'.encode('ascii'))
    except InvalidSignature:
        raise OfflineLicenseError(OfflineLicenseErrorCode.BAD_SIGNATURE) from None

    # 5-7. Claims, compared exactly (no trimming or case folding).
    if payload.get('type') != 'offline':
        raise OfflineLicenseError(OfflineLicenseErrorCode.WRONG_TYPE)
    if payload.get('productId') != product_id:
        raise OfflineLicenseError(OfflineLicenseErrorCode.WRONG_PRODUCT)
    if payload.get('machineCode') != machine_code:
        raise OfflineLicenseError(OfflineLicenseErrorCode.WRONG_MACHINE)

    # 8. Shape of the remaining claims, then 9. expiry.
    exp = payload.get('exp')
    sub = payload.get('sub')
    iat = payload.get('iat')
    expires_at = _to_datetime(exp) if _is_number(exp) else None
    if expires_at is None:
        raise OfflineLicenseError(OfflineLicenseErrorCode.MALFORMED)
    if not isinstance(sub, str) or not sub:
        raise OfflineLicenseError(OfflineLicenseErrorCode.MALFORMED)
    if not now.timestamp() < exp + clock_skew:
        raise OfflineLicenseError(OfflineLicenseErrorCode.EXPIRED)

    return OfflineLicense(
        license_key=sub,
        product_id=product_id,
        machine_code=machine_code,
        key_id=kid,
        issued_at=_to_datetime(iat) if _is_number(iat) else None,
        expires_at=expires_at,
    )
