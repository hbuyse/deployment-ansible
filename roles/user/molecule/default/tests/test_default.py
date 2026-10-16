import hashlib
from pathlib import Path

ROLE_DIR = Path(__file__).resolve().parents[3]
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _face_sha256():
    return hashlib.sha256((ROLE_DIR / "files" / "face.png").read_bytes()).hexdigest()


def _sha256(host, path):
    return host.check_output(f"sha256sum {path}").split()[0]


def test_face_in_home_directory(host):
    """The face image is copied to ~/.face."""
    face = host.file("/root/.face")
    assert face.is_file
    assert oct(face.mode) == "0o644"
    assert _sha256(host, face.path) == _face_sha256()


def test_face_for_accounts_service(host):
    """The face image is copied to the AccountsService icons directory, named after the user."""
    icon = host.file("/var/lib/AccountsService/icons/root")
    assert icon.is_file
    assert oct(icon.mode) == "0o644"
    assert _sha256(host, icon.path) == _face_sha256()


def test_face_is_a_png(host):
    """The deployed image is a PNG."""
    assert host.check_output("head -c 8 /root/.face | od -An -c | tr -d ' '") == "211PNG\\r\\n032\\n"
