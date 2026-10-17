from pathlib import Path

ROLE_DIR = Path(__file__).resolve().parents[3]
SYSTEMCTL = "XDG_RUNTIME_DIR=/run/user/0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/0/bus systemctl --user"


def test_packages(host):
    """swayidle and its dependency swaylock are installed."""
    assert host.package("swayidle").is_installed
    assert host.package("swaylock").is_installed


def test_configuration(host):
    """The configuration of swayidle is deployed."""
    config = host.file("/root/.config/swayidle/config")
    assert config.is_file
    assert config.content_string == (ROLE_DIR / "files" / "config").read_text()


def test_service_file_and_state(host):
    """The unit file is deployed and the handler enabled the user service."""
    unit = host.file("/root/.config/systemd/user/swayidle.service")
    assert unit.is_file
    assert unit.content_string == (ROLE_DIR / "files" / "swayidle.service").read_text()
    assert host.run(f"{SYSTEMCTL} is-enabled swayidle").stdout.strip() == "enabled"


def test_dependency_was_applied(host):
    """The swaylock role ran first: its configuration and unit file exist."""
    assert host.file("/root/.config/swaylock/config").is_file
    assert host.file("/root/.config/systemd/user/swaylock.service").is_file
