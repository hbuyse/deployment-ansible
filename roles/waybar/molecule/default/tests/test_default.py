import re
from pathlib import Path

ROLE_DIR = Path(__file__).resolve().parents[3]
SYSTEMCTL = "XDG_RUNTIME_DIR=/run/user/0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/0/bus systemctl --user"
CONFIG = "/root/.config/waybar"


def test_waybar_runs(host):
    """waybar is installed and reports its version."""
    cmd = host.run("waybar --version")
    assert cmd.rc == 0, cmd.stderr
    assert re.search(r"\d+\.\d+\.\d+", cmd.stdout)


def test_static_configuration(host):
    """Every static file of the role is deployed in ~/.config/waybar."""
    files = [path for path in (ROLE_DIR / "files" / "config").rglob("*") if path.is_file()]
    assert files
    for source in files:
        deployed = host.file(f"{CONFIG}/{source.relative_to(ROLE_DIR / 'files' / 'config')}")
        assert deployed.is_file, source
        assert deployed.content_string == source.read_text(), source


def test_style_sheet_is_generated(host):
    """The SCSS file is compiled to CSS."""
    css = host.file(f"{CONFIG}/style.css")
    assert css.is_file
    assert css.size > 0


def test_dynamic_configuration_is_rendered(host):
    """The templated configurations have no leftover Jinja (playerctl formats like {{status}} are meant to stay)."""
    for name in ("sway.jsonc", "hyprland.jsonc", "modules.jsonc"):
        config = host.file(f"{CONFIG}/{name}")
        assert config.is_file, name
        assert "{{ " not in config.content_string, name
        assert "{%" not in config.content_string, name


def test_python_virtualenv(host):
    """The virtualenv of the scripts has its packages."""
    pip = host.run(f"{CONFIG}/scripts/.venv/bin/python -c 'import requests, tabulate, gi'")
    assert pip.rc == 0, pip.stderr


def test_service(host):
    """The unit file is deployed under its user name and the handler enabled the service."""
    assert host.file("/root/.config/systemd/user/waybar-user.service").is_file
    assert not host.file("/root/.config/systemd/user/waybar.service").exists
    assert host.run(f"{SYSTEMCTL} is-enabled waybar-user").stdout.strip() == "enabled"
