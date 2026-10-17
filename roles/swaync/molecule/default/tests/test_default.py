import re
from pathlib import Path

ROLE_DIR = Path(__file__).resolve().parents[3]
SYSTEMCTL = "XDG_RUNTIME_DIR=/run/user/0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/0/bus systemctl --user"
CONFIG = "/root/.config/swaync"


def test_swaync_runs(host):
    """swaync is installed and reports its version."""
    cmd = host.run("DISPLAY=:99 swaync --version")
    assert cmd.rc == 0, cmd.stderr
    assert re.search(r"\d+\.\d+\.\d+", cmd.stdout)


def test_static_configuration(host):
    """Every static file of the role is deployed in ~/.config/swaync."""
    files = [path for path in (ROLE_DIR / "files" / "config").rglob("*") if path.is_file()]
    for source in files:
        deployed = host.file(f"{CONFIG}/{source.relative_to(ROLE_DIR / 'files' / 'config')}")
        assert deployed.is_file, source


def test_json_configuration_is_rendered(host):
    """config.json is generated from its template and is valid JSON."""
    config = host.file(f"{CONFIG}/config.json")
    assert config.is_file
    assert "{{" not in config.content_string
    import json
    json.loads(config.content_string)


def test_theme_and_style_sheet(host):
    """The Catppuccin palette is downloaded and the style sheet is compiled."""
    assert host.file(f"{CONFIG}/themes/catppuccin.css").is_file
    css = host.file(f"{CONFIG}/style.css")
    assert css.is_file
    assert css.size > 0


def test_service(host):
    """The unit file is rendered and the handler enabled the user service."""
    unit = host.file("/root/.config/systemd/user/swaync.service")
    assert unit.is_file
    assert "{{" not in unit.content_string
    assert host.run(f"{SYSTEMCTL} is-enabled swaync").stdout.strip() == "enabled"
