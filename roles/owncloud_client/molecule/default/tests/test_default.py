from pathlib import Path

ROLE_DIR = Path(__file__).resolve().parents[3]
SYSTEMCTL = "XDG_RUNTIME_DIR=/run/user/0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/0/bus systemctl --user"


def test_repository(host):
    """The ownCloud apt repository of the client is configured for the distribution."""
    release = host.check_output(". /etc/os-release && echo ${ID}_${VERSION_ID}")
    expected = {"debian_12": "Debian_12", "ubuntu_24.04": "Ubuntu_24.04"}[release]
    source = host.file("/etc/apt/sources.list.d/owncloud-client.sources")
    assert source.is_file
    assert f"download.owncloud.com/desktop/ownCloud/stable/6.0/linux/{expected}/" in source.content_string


def test_package(host):
    """owncloud-client is installed from that repository."""
    assert host.package("owncloud-client").is_installed
    assert "download.owncloud.com" in host.check_output("apt-cache policy owncloud-client")


def test_service_file(host):
    """The unit file of the user service is deployed."""
    unit = host.file("/root/.config/systemd/user/owncloud-client.service")
    assert unit.is_file
    assert unit.content_string == (ROLE_DIR / "files" / "owncloud-client.service").read_text()


def test_service_is_enabled(host):
    """The handler enabled the user service."""
    cmd = host.run(f"{SYSTEMCTL} is-enabled owncloud-client")
    assert cmd.stdout.strip() == "enabled", cmd.stderr
