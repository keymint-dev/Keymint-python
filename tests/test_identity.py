import hashlib
import os
import sys
import warnings

import pytest

from keymint import InstallationIdError, InstallationIdWarning, identity


@pytest.fixture(autouse=True)
def reset_warning_flag(monkeypatch):
    monkeypatch.setattr(identity, "_unsaved_warning_emitted", False)
    monkeypatch.setattr(identity, "get_machine_id", lambda: "anchor")


def unwritable_path(tmp_path):
    # The parent "directory" is a regular file, so mkdir and write fail
    # on every platform, even when the tests run as root.
    blocker = tmp_path / "not-a-directory"
    blocker.write_text("x")
    return blocker / "installation-id"


def test_saves_the_id_and_returns_the_same_value_next_time(tmp_path):
    path = tmp_path / "nested" / "installation-id"
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        first = identity.get_or_create_installation_id(str(path))
        second = identity.get_or_create_installation_id(str(path))
    assert path.exists()
    assert first == second
    assert first == hashlib.sha256(path.read_text().strip().encode()).hexdigest()


def test_strict_mode_saves_normally(tmp_path):
    path = tmp_path / "installation-id"
    value = identity.get_or_create_installation_id(str(path), require_persisted=True)
    assert value == identity.get_or_create_installation_id(str(path), require_persisted=True)


def test_existing_file_is_reused(tmp_path):
    path = tmp_path / "installation-id"
    path.write_text("existing-id\n")
    expected = hashlib.sha256(b"existing-id").hexdigest()
    assert identity.get_or_create_installation_id(str(path)) == expected
    assert identity.get_or_create_installation_id(str(path), require_persisted=True) == expected
    assert path.read_text() == "existing-id\n"


def test_unwritable_default_returns_an_id_and_warns_once(tmp_path):
    path = unwritable_path(tmp_path)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        first = identity.get_or_create_installation_id(str(path))
        second = identity.get_or_create_installation_id(str(path))
    assert len(first) == 64 and len(second) == 64
    assert first != second  # nothing was saved
    relevant = [w for w in caught if issubclass(w.category, InstallationIdWarning)]
    assert len(relevant) == 1
    assert issubclass(relevant[0].category, RuntimeWarning)
    assert str(path) in str(relevant[0].message)
    assert relevant[0].filename == __file__


def test_unwritable_strict_raises(tmp_path):
    path = unwritable_path(tmp_path)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        with pytest.raises(InstallationIdError) as excinfo:
            identity.get_or_create_installation_id(str(path), require_persisted=True)
    assert excinfo.value.path == str(path)
    assert str(path) in str(excinfo.value)
    assert isinstance(excinfo.value, OSError)


@pytest.mark.skipif(sys.platform == "win32" or os.geteuid() == 0, reason="needs POSIX permissions as non-root")
def test_read_only_directory(tmp_path):
    directory = tmp_path / "ro"
    directory.mkdir()
    directory.chmod(0o500)
    path = directory / "installation-id"
    try:
        with pytest.warns(InstallationIdWarning):
            assert len(identity.get_or_create_installation_id(str(path))) == 64
        with pytest.raises(InstallationIdError):
            identity.get_or_create_installation_id(str(path), require_persisted=True)
    finally:
        directory.chmod(0o700)


def test_read_back_mismatch_raises_in_strict_mode(tmp_path, monkeypatch):
    path = tmp_path / "installation-id"
    original_write = type(path).write_text

    def lossy_write(self, data, *args, **kwargs):
        return original_write(self, data[:-1], *args, **kwargs)

    monkeypatch.setattr(type(path), "write_text", lossy_write)
    with pytest.raises(InstallationIdError):
        identity.get_or_create_installation_id(str(path), require_persisted=True)
