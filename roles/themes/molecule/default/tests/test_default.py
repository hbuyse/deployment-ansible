def test_gtk_directories(host):
    """The directories of the GTK themes and settings exist."""
    for path in ("/root/.local/share/themes", "/root/.config/gtk-3.0", "/root/.config/gtk-4.0"):
        assert host.file(path).is_directory, path


def test_dependencies(host):
    """The icon theme that the role depends on is installed."""
    assert host.package("papirus-icon-theme").is_installed


def test_matcha_theme_is_installed(host):
    """The Matcha theme of the latest release is installed in ~/.local/share/themes."""
    themes = host.file("/root/.local/share/themes").listdir()
    assert any(name.startswith("Matcha") for name in themes), themes
