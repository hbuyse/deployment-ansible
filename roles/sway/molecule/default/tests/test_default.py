from pathlib import Path

ROLE_DIR = Path(__file__).resolve().parents[3]
SYSTEMCTL = "XDG_RUNTIME_DIR=/run/user/0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/0/bus systemctl --user"
CONFIG = "/root/.config/sway"


def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()


def test_packages(host):
    """Sway, the screenshot tools and the file manager are installed."""
    names = ["sway", "grim", "slurp", "thunar"]
    if _os_id(host) != "arch":
        names.append("lxsession")  # lxsession-gtk3, in the AUR, on Arch
    for name in names:
        assert host.package(name).is_installed, name


def test_static_configuration(host):
    """Every static file of the role is deployed in ~/.config/sway."""
    files = [path for path in (ROLE_DIR / "files" / "sway").rglob("*") if path.is_file()]
    assert files
    for source in files:
        deployed = host.file(f"{CONFIG}/{source.relative_to(ROLE_DIR / 'files' / 'sway')}")
        assert deployed.is_file, source
        assert deployed.content_string == source.read_text(), source


def test_dynamic_configuration_is_rendered(host):
    """The templated files have no leftover Jinja."""
    for name in ("variables", "config.d/01-default-screen.conf", "config.d/99-autostart.conf"):
        config = host.file(f"{CONFIG}/{name}")
        assert config.is_file, name
        assert "{{" not in config.content_string, name
        assert "{%" not in config.content_string, name


def test_session_units(host):
    """The session target and the polkit agent unit are deployed, and the agent is enabled."""
    for name in ("lxpolkit.service", "sway-session.target"):
        assert host.file(f"/root/.config/systemd/user/{name}").is_file, name
    assert host.run(f"{SYSTEMCTL} is-enabled lxpolkit").stdout.strip() == "enabled"


def test_preferred_terminal_script(host):
    """The preferred-terminal script is deployed and executable."""
    script = host.file("/root/.local/bin/preferred-terminal")
    assert script.is_file
    assert oct(script.mode) == "0o755"
