def test_appimage(host):
    """The AppImage is downloaded in ~/.local/bin, executable, and is an ELF file."""
    appimage = host.file("/root/.local/bin/bitwarden")
    assert appimage.is_file
    assert oct(appimage.mode) == "0o755"
    assert appimage.size > 10 * 1024 * 1024
    assert host.check_output("head -c 4 /root/.local/bin/bitwarden | od -An -c | tr -d ' '") == "177ELF"


def test_desktop_file(host):
    """The desktop file is downloaded in ~/.local/share/applications."""
    desktop = host.file("/root/.local/share/applications/com.bitwarden.desktop.desktop")
    assert desktop.is_file
    assert oct(desktop.mode) == "0o644"
    assert "Name=Bitwarden" in desktop.content_string
