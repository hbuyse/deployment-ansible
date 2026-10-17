from pathlib import Path

ROLE_DIR = Path(__file__).resolve().parents[3]
CONFIG = "/root/.config/fuzzel"


def test_fuzzel_package(host):
    """fuzzel is installed from the package manager."""
    assert host.package("fuzzel").is_installed


def test_fuzzel_runs(host):
    """fuzzel reports its version."""
    cmd = host.run("fuzzel --version")
    assert cmd.rc == 0, cmd.stderr
    assert "fuzzel" in cmd.stdout


def test_keybindings(host):
    """The key bindings of the role are deployed."""
    keybindings = host.file(f"{CONFIG}/keybindings.ini")
    assert keybindings.is_file
    assert keybindings.content_string == (ROLE_DIR / "files" / "keybindings.ini").read_text()


def test_configuration_is_rendered(host):
    """fuzzel.ini is generated from its template and includes the key bindings and the theme."""
    config = host.file(f"{CONFIG}/fuzzel.ini")
    assert config.is_file
    assert "{{" not in config.content_string
    assert "include=~/.config/fuzzel/keybindings.ini" in config.content_string
    assert "include=~/.config/fuzzel/catppuccin-mocha.ini" in config.content_string


def test_catppuccin_theme(host):
    """The Catppuccin theme is downloaded."""
    theme = host.file(f"{CONFIG}/catppuccin-mocha.ini")
    assert theme.is_file
    assert "[colors]" in theme.content_string
