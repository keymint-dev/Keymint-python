import base64
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

from keymint import (
    OfflineLicense,
    OfflineLicenseError,
    OfflineLicenseErrorCode,
    verify_offline_license,
)
from keymint.offline import _key_id, _load_public_key

FIXTURES = json.loads(
    (Path(__file__).parent / "fixtures" / "offline-license-fixtures.json").read_text(encoding="utf-8")
)
PUBLIC_KEYS = FIXTURES["publicKeys"]
VALID_CASE = FIXTURES["cases"][0]
PRODUCT_ID = VALID_CASE["options"]["productId"]
MACHINE_CODE = VALID_CASE["options"]["machineCode"]
NOW = datetime.fromtimestamp(VALID_CASE["options"]["now"], tz=timezone.utc)


def unix(value):
    return None if value is None else value.timestamp()


def verify_case(case):
    options = case["options"]
    kwargs = {
        "public_keys": PUBLIC_KEYS,
        "product_id": options["productId"],
        "machine_code": options["machineCode"],
        "now": datetime.fromtimestamp(options["now"], tz=timezone.utc),
    }
    if "clockSkew" in options:
        kwargs["clock_skew"] = options["clockSkew"]
    return verify_offline_license(case["input"], **kwargs)


def test_fixture_file_has_all_cases():
    assert len(FIXTURES["cases"]) == 34


def test_key_ids_match_fixtures():
    assert [_key_id(_load_public_key(pem, i)) for i, pem in enumerate(PUBLIC_KEYS)] == FIXTURES["keyIds"]


@pytest.mark.parametrize("case", FIXTURES["cases"], ids=[c["name"] for c in FIXTURES["cases"]])
def test_shared_fixture(case):
    expect = case["expect"]
    if expect["valid"]:
        result = verify_case(case)
        expected = expect["license"]
        assert isinstance(result, OfflineLicense)
        assert result.license_key == expected["licenseKey"]
        assert result.product_id == expected["productId"]
        assert result.machine_code == expected["machineCode"]
        assert result.key_id == expected["keyId"]
        assert unix(result.issued_at) == expected["issuedAt"]
        assert unix(result.expires_at) == expected["expiresAt"]
        assert result.expires_at.tzinfo is timezone.utc
    else:
        with pytest.raises(OfflineLicenseError) as excinfo:
            verify_case(case)
        assert excinfo.value.code == expect["error"]
        assert isinstance(excinfo.value.code, OfflineLicenseErrorCode)


def test_errors_never_contain_the_license_key():
    case = next(c for c in FIXTURES["cases"] if c["name"] == "wrong product")
    with pytest.raises(OfflineLicenseError) as excinfo:
        verify_case(case)
    assert "KM-ABCD" not in str(excinfo.value)
    assert "KM-ABCD" not in repr(excinfo.value)


def test_repr_hides_the_license_key():
    result = verify_case(VALID_CASE)
    assert "KM-ABCD" not in repr(result)


def test_accepts_now_in_another_timezone():
    from datetime import timedelta

    tz = timezone(timedelta(hours=-5))
    result = verify_offline_license(
        VALID_CASE["input"], public_keys=PUBLIC_KEYS, product_id=PRODUCT_ID,
        machine_code=MACHINE_CODE, now=NOW.astimezone(tz),
    )
    assert result.license_key == "KM-ABCD-1234-EFGH-5678"


# ─── Tokens signed here, for Python-specific edge cases ─────────────────

def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def sign(payload_json: str):
    private_key = ed25519.Ed25519PrivateKey.generate()
    pem = private_key.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo).decode()
    header = json.dumps({"alg": "EdDSA", "kid": _key_id(private_key.public_key())})
    signing_input = f"{b64url(header.encode())}.{b64url(payload_json.encode())}"
    token = f"{signing_input}.{b64url(private_key.sign(signing_input.encode('ascii')))}"
    return token, pem


def claims(**overrides):
    payload = {
        "productId": PRODUCT_ID, "machineCode": MACHINE_CODE, "type": "offline",
        "iat": 1799913600, "exp": 1802592000, "sub": "KM-TEST",
    }
    payload.update(overrides)
    return json.dumps(payload)


def verify_signed(payload_json: str):
    token, pem = sign(payload_json)
    return verify_offline_license(
        token, public_keys=[pem], product_id=PRODUCT_ID, machine_code=MACHINE_CODE, now=NOW,
    )


@pytest.mark.parametrize("payload_json", [
    claims(exp=True),
    claims(exp=None),
    claims(exp="1802592000"),
    claims(sub=""),
    claims(sub=123),
    claims().replace("1802592000", "NaN"),
    claims().replace("1802592000", "Infinity"),
    claims().replace("1802592000", "1e400"),
    claims().replace("1802592000", "1" + "0" * 400),
], ids=["bool", "null", "string", "empty sub", "number sub", "NaN", "Infinity", "huge float", "huge int"])
def test_bad_exp_or_sub_is_malformed(payload_json):
    with pytest.raises(OfflineLicenseError) as excinfo:
        verify_signed(payload_json)
    assert excinfo.value.code == "malformed"


def test_bool_iat_is_not_returned():
    assert verify_signed(claims(iat=True)).issued_at is None


def test_missing_iat_is_none():
    payload = json.loads(claims())
    del payload["iat"]
    assert verify_signed(json.dumps(payload)).issued_at is None


def test_float_exp_is_accepted():
    result = verify_signed(claims(exp=1802592000.5))
    assert unix(result.expires_at) == 1802592000.5


def test_trailing_newline_in_a_segment_is_malformed():
    token, pem = sign(claims())
    header, payload, signature = token.split(".")
    with pytest.raises(OfflineLicenseError) as excinfo:
        verify_offline_license(
            f"{header}\n.{payload}.{signature}", public_keys=[pem],
            product_id=PRODUCT_ID, machine_code=MACHINE_CODE, now=NOW,
        )
    assert excinfo.value.code == "malformed"


@pytest.mark.parametrize("value", [
    '{"signedKey":' + "[" * 100_000,
    b64url(b'{"a":' + b"[" * 100_000) + ".e30.",
], ids=[".lic", "token header"])
def test_deeply_nested_json_is_malformed(value):
    with pytest.raises(OfflineLicenseError) as excinfo:
        verify_offline_license(
            value, public_keys=PUBLIC_KEYS, product_id=PRODUCT_ID, machine_code=MACHINE_CODE, now=NOW,
        )
    assert excinfo.value.code == "malformed"


# ─── Argument errors ────────────────────────────────────────────────────

def rsa_public_pem():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return key.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo).decode()


def ed25519_private_pem():
    key = ed25519.Ed25519PrivateKey.generate()
    return key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()).decode()


def call(**overrides):
    kwargs = {
        "public_keys": PUBLIC_KEYS, "product_id": PRODUCT_ID,
        "machine_code": MACHINE_CODE, "now": NOW,
    }
    kwargs.update(overrides)
    return verify_offline_license(VALID_CASE["input"], **kwargs)


@pytest.mark.parametrize("overrides", [
    {"public_keys": []},
    {"public_keys": ["not a pem"]},
    {"public_keys": ["-----BEGIN PUBLIC KEY-----\nAAAA\n-----END PUBLIC KEY-----\n"]},
    {"public_keys": [rsa_public_pem()]},
    {"public_keys": [ed25519_private_pem()]},
    {"product_id": ""},
    {"machine_code": ""},
    {"clock_skew": -1},
    {"clock_skew": 3601},
    {"clock_skew": float("nan")},
    {"now": datetime(2027, 1, 15, 8, 0, 0)},
], ids=[
    "no keys", "garbage pem", "truncated pem", "rsa key", "private key",
    "empty product", "empty machine", "negative skew", "skew over an hour", "nan skew", "naive now",
])
def test_bad_arguments_raise_value_error(overrides):
    with pytest.raises(ValueError):
        call(**overrides)


@pytest.mark.parametrize("overrides", [
    {"public_keys": PUBLIC_KEYS[0]},
    {"public_keys": [b"bytes"]},
    {"product_id": None},
    {"machine_code": 1},
    {"clock_skew": True},
    {"clock_skew": "60"},
    {"now": 1800000000},
], ids=["single string", "bytes key", "product none", "machine int", "bool skew", "string skew", "int now"])
def test_wrong_argument_types_raise_type_error(overrides):
    with pytest.raises(TypeError):
        call(**overrides)


def test_clock_skew_bounds_are_inclusive():
    assert call(clock_skew=0).license_key
    assert call(clock_skew=3600).license_key


def test_rsa_key_error_names_ed25519():
    with pytest.raises(ValueError, match="Ed25519"):
        call(public_keys=[rsa_public_pem()])
