from pathlib import Path

ROLE_DIR = Path(__file__).resolve().parents[3]
SYSTEMCTL = "XDG_RUNTIME_DIR=/run/user/0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/0/bus systemctl --user"
CONFIG = "/root/.config/kanshi"


def test_kanshi_package(host):
    """kanshi is installed from the package manager."""
    assert host.package("kanshi").is_installed
    assert host.exists("kanshi")


def test_static_files(host):
    """The root configuration and the notification script are deployed."""
    config = host.file(f"{CONFIG}/config")
    assert config.is_file
    assert config.content_string == (ROLE_DIR / "files" / "config").read_text()
    script = host.file(f"{CONFIG}/notify.sh")
    assert script.is_file
    assert oct(script.mode) == "0o755"


def test_profiles_are_rendered(host):
    """The home and single screen profiles are generated, the work one only with kanshi_work_confs."""
    for name in ("home", "one-screen"):
        profile = host.file(f"{CONFIG}/config.d/{name}")
        assert profile.is_file, name
        assert "{{" not in profile.content_string, name
        assert "{%" not in profile.content_string, name
    assert not host.file(f"{CONFIG}/config.d/work").exists


def test_service(host):
    """The unit file is deployed and the handler enabled the user service."""
    assert host.file("/root/.config/systemd/user/kanshi.service").is_file
    assert host.run(f"{SYSTEMCTL} is-enabled kanshi").stdout.strip() == "enabled"
