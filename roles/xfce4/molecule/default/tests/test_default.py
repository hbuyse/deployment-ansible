from pathlib import Path

ROLE_DIR = Path(__file__).resolve().parents[3]
COLORSCHEMES = "/root/.local/share/xfce4/terminal/colorschemes"
CONFIG = "/root/.config/xfce4"


def test_catppuccin_terminal_themes(host):
    """The four Catppuccin themes of xfce4-terminal are downloaded."""
    for flavour in ("frappe", "latte", "macchiato", "mocha"):
        theme = host.file(f"{COLORSCHEMES}/catppuccin-{flavour}.theme")
        assert theme.is_file, flavour
        assert oct(theme.mode) == "0o644", flavour
        assert "[Scheme]" in theme.content_string, flavour


def test_static_configuration_files(host):
    """Every file of the role is copied unchanged in ~/.config/xfce4."""
    files = [path for path in (ROLE_DIR / "files").rglob("*") if path.is_file()]
    assert files
    for source in files:
        deployed = host.file(f"{CONFIG}/{source.relative_to(ROLE_DIR / 'files')}")
        assert deployed.is_file, source
        assert deployed.content_string == source.read_text(), source


def test_desktop_configuration_is_rendered(host):
    """The desktop configuration is generated from its template, with no leftover Jinja."""
    desktop = host.file(f"{CONFIG}/xfconf/xfce-perchannel-xml/xfce4-desktop.xml")
    assert desktop.is_file
    assert "{{" not in desktop.content_string
    assert "{%" not in desktop.content_string
