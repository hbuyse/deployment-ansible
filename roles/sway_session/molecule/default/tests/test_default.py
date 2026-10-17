from pathlib import Path

ROLE_DIR = Path(__file__).resolve().parents[3]


def test_session_target(host):
    """The target that the services of the desktop are part of is deployed in the user systemd directory."""
    target = host.file("/root/.config/systemd/user/sway-session.target")
    assert target.is_file
    assert oct(target.mode) == "0o644"
    assert target.content_string == (ROLE_DIR / "files" / "sway-session.target").read_text()


def test_systemd_directory(host):
    """The directory of the user units exists."""
    assert host.file("/root/.config/systemd/user").is_directory
