from pathlib import Path

ROLE_DIR = Path(__file__).resolve().parents[3]


def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()

SYSTEMCTL = "XDG_RUNTIME_DIR=/run/user/0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/0/bus systemctl --user"


def test_packages(host):
    """The client (nextcloud-desktop on Debian) and the keyring tools are installed."""
    client = "nextcloud-desktop" if _os_id(host) == "debian" else "nextcloud-client"
    for name in (client, "gnome-keyring", "seahorse"):
        assert host.package(name).is_installed, name


def test_ppa_on_ubuntu(host):
    """Ubuntu uses the Nextcloud PPA."""
    source = host.file("/etc/apt/sources.list.d/nextcloud-devs.sources")
    if _os_id(host) == "ubuntu":
        assert "nextcloud-devs/client/ubuntu" in source.content_string
    else:
        assert not source.exists


def test_service_file(host):
    """The unit file of the user service is deployed."""
    unit = host.file("/root/.config/systemd/user/nextcloud.service")
    assert unit.is_file
    assert unit.content_string == (ROLE_DIR / "files" / "nextcloud.service").read_text()


def test_service_is_enabled(host):
    """The handler enabled the user service."""
    cmd = host.run(f"{SYSTEMCTL} is-enabled nextcloud")
    assert cmd.stdout.strip() == "enabled", cmd.stderr
