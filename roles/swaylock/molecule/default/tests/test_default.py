from pathlib import Path

ROLE_DIR = Path(__file__).resolve().parents[3]


def test_swaylock_package(host):
    """swaylock is installed from the package manager."""
    assert host.package("swaylock").is_installed
    assert host.exists("swaylock")


def test_configuration_is_rendered(host):
    """The configuration is generated from its template, with the locker image of the user."""
    config = host.file("/root/.config/swaylock/config")
    assert config.is_file
    assert oct(config.mode) == "0o644"
    assert "{{" not in config.content_string
    assert "image=/root/.local/share/backgrounds/locker.png" in config.content_string


def test_service_file(host):
    """The unit file of the user service is deployed."""
    unit = host.file("/root/.config/systemd/user/swaylock.service")
    assert unit.is_file
    assert unit.content_string == (ROLE_DIR / "files" / "swaylock.service").read_text()
