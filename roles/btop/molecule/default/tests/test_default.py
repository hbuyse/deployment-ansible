from pathlib import Path

ROLE_DIR = Path(__file__).resolve().parents[3]


def test_btop_package(host):
    """btop is installed from the package manager."""
    assert host.package("btop").is_installed


def test_btop_command(host):
    """The btop command is installed (it cannot be started in a container: it has file capabilities)."""
    assert host.exists("btop")


def test_btop_configuration(host):
    """The configuration of the role is deployed in ~/.config/btop."""
    config = host.file("/root/.config/btop/btop.conf")
    assert config.is_file
    assert oct(config.mode) == "0o644"
    assert config.content_string == (ROLE_DIR / "files" / "btop.conf").read_text()


def test_catppuccin_themes(host):
    """The Catppuccin themes of the latest release are unpacked in ~/.config/btop/themes."""
    themes = host.file("/root/.config/btop/themes")
    assert themes.is_directory
    names = themes.listdir()
    assert any(name.startswith("catppuccin_mocha") for name in names), names
