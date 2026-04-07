"""
Machine identity utilities for the Keymint Python SDK.

Provides two methods for identifying machines:
- get_machine_id(): Best-effort hardware fingerprint (may fail or collide).
- get_or_create_installation_id(): Guaranteed-stable persistent identity.
"""

import hashlib
import os
import platform
import subprocess
import uuid
import re
import time
from pathlib import Path
from typing import Optional


# ─── Garbage Detection ──────────────────────────────────────────────────

_GARBAGE_PATTERNS = [
    re.compile(r'^0+$'),
    re.compile(r'^f+$'),
    'ffffffffffffffffffffffffffffffff',
    '03000200040005000006000700080009',
    'defaultstring',
    'tobefilledbyoem',
    'notapplicable',
    'notspecified',
    'systemserialnum',
    'none',
]


def _is_garbage_id(raw_id: str) -> bool:
    """Returns True if the ID is a known default/garbage value."""
    normalized = re.sub(r'[-:\s._]', '', raw_id.lower())
    for pattern in _GARBAGE_PATTERNS:
        if isinstance(pattern, re.Pattern):
            if pattern.match(normalized):
                return True
        else:
            if normalized == pattern or pattern in normalized:
                return True
    return False


def _hash(value: str) -> str:
    """SHA-256 hash a string into a 64-char hex digest."""
    return hashlib.sha256(value.lower().strip().encode('utf-8')).hexdigest()


# ─── Fingerprint Layers ────────────────────────────────────────────────

def _get_bios_uuid() -> Optional[str]:
    """Layer 1: BIOS / Hardware UUID."""
    system = platform.system()
    try:
        if system == 'Windows':
            result = subprocess.run(
                ['powershell.exe', '-Command',
                 '(Get-CimInstance Win32_ComputerSystemProduct).UUID'],
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip() or None
        elif system == 'Darwin':
            result = subprocess.run(
                ['bash', '-c',
                 "ioreg -rd1 -c IOPlatformExpertDevice | grep IOPlatformUUID | awk -F'\"' '{print $4}'"],
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip() or None
        elif system == 'Linux':
            path = '/sys/class/dmi/id/product_uuid'
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return f.read().strip() or None
    except Exception:
        pass
    return None


def _get_os_machine_id() -> Optional[str]:
    """Layer 2: OS-level persistent machine ID."""
    system = platform.system()
    try:
        if system == 'Windows':
            result = subprocess.run(
                ['powershell.exe', '-Command',
                 "(Get-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Cryptography' -Name MachineGuid).MachineGuid"],
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip() or None
        elif system == 'Darwin':
            result = subprocess.run(
                ['bash', '-c',
                 "ioreg -rd1 -c IOPlatformExpertDevice | grep IOPlatformSerialNumber | awk -F'\"' '{print $4}'"],
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip() or None
        elif system == 'Linux':
            for path in ['/etc/machine-id', '/var/lib/dbus/machine-id']:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        value = f.read().strip()
                        if value:
                            return value
    except Exception:
        pass
    return None


def _get_primary_mac() -> Optional[str]:
    """Layer 3: Primary network interface MAC address."""
    try:
        import socket
        import fcntl
        import struct
    except ImportError:
        pass

    # Cross-platform fallback using uuid.getnode()
    try:
        mac = uuid.getnode()
        # uuid.getnode() returns a random MAC if it can't find one (bit 0 set)
        if (mac >> 40) & 1 == 0:
            mac_str = ':'.join(f'{(mac >> (8 * i)) & 0xff:02x}' for i in reversed(range(6)))
            if mac_str != '00:00:00:00:00:00':
                return mac_str
    except Exception:
        pass
    return None


# ─── Public API ─────────────────────────────────────────────────────────

def get_machine_id() -> Optional[str]:
    """
    Best-effort hardware fingerprint. Attempts to read the machine's
    BIOS/System UUID, then falls back through OS-level IDs and network
    interfaces. May return different values after hardware changes or
    OS reinstalls.

    Use this for logging, display, or secondary validation.
    For activation host_id, prefer get_or_create_installation_id().

    Returns:
        A SHA-256 hashed 64-character hex string, or None if every layer failed.
    """
    layers = [_get_bios_uuid, _get_os_machine_id, _get_primary_mac]

    for layer in layers:
        try:
            raw = layer()
            if raw and len(raw) > 4 and not _is_garbage_id(raw):
                return _hash(raw)
        except Exception:
            continue

    return None


def get_or_create_installation_id(storage_path: Optional[str] = None) -> str:
    """
    Returns a guaranteed-unique, guaranteed-stable installation identifier.
    On first call, generates a UUIDv4 seeded with whatever hardware info
    is available and persists it to disk. Every subsequent call returns the
    same value.

    This is the **recommended** value to pass as `host_id` when activating
    a license key.

    Args:
        storage_path: Optional custom path for the persistence file.
            Defaults to ~/.keymint/installation-id.

    Returns:
        A SHA-256 hashed 64-character hex string.

    Raises:
        OSError: If the file cannot be read or written.
    """
    file_path = Path(storage_path) if storage_path else Path.home() / '.keymint' / 'installation-id'

    # 1. If the file exists, trust it
    if file_path.exists():
        stored = file_path.read_text(encoding='utf-8').strip()
        if stored:
            return hashlib.sha256(stored.encode('utf-8')).hexdigest()

    # 2. Generate a new installation ID, anchored to hardware when possible
    hardware_anchor = get_machine_id() or ''
    new_uuid = str(uuid.uuid4())
    composite_id = f'{new_uuid}:{hardware_anchor}:{int(time.time() * 1000)}'

    # 3. Persist it
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(composite_id, encoding='utf-8')

    return hashlib.sha256(composite_id.encode('utf-8')).hexdigest()
