from pathlib import Path

ROLE_DIR = Path(__file__).resolve().parents[3]
CONFIG = "/root/.config/wofi"


def test_wofi_package(host):
    """wofi is installed from the package manager."""
    assert host.package("wofi").is_installed
    assert host.exists("wofi")


def test_configuration(host):
    """The configuration of the role is deployed in ~/.config/wofi."""
    config = host.file(f"{CONFIG}/config")
    assert config.is_file
    assert oct(config.mode) == "0o644"
    assert config.content_string == (ROLE_DIR / "files" / "config").read_text()


def test_style_sheet_is_generated(host):
    """The SCSS file of the role is compiled to CSS."""
    css = host.file(f"{CONFIG}/style.css")
    assert css.is_file
    assert css.size > 0
    assert "@import" not in css.content_string
    assert "{" in css.content_string
