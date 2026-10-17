from pathlib import Path

ROLE_DIR = Path(__file__).resolve().parents[3]
CONFIG = "/root/.config/xdg-desktop-portal-wlr"


def test_packages(host):
    """The wlroots and GTK portals are installed."""
    assert host.package("xdg-desktop-portal-wlr").is_installed
    assert host.package("xdg-desktop-portal-gtk").is_installed


def test_configuration(host):
    """The configuration of the wlroots portal is deployed."""
    config = host.file(f"{CONFIG}/config")
    assert config.is_file
    assert oct(config.mode) == "0o644"
    assert config.content_string == (ROLE_DIR / "files" / "xdg-desktop-portal-wlr" / "config").read_text()


def test_script_is_executable(host):
    """The script used by the portal is deployed and executable."""
    script = host.file(f"{CONFIG}/script.sh")
    assert script.is_file
    assert oct(script.mode) == "0o755"
    assert script.content_string == (ROLE_DIR / "files" / "xdg-desktop-portal-wlr" / "script.sh").read_text()
