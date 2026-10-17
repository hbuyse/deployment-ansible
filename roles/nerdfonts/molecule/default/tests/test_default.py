

def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()


def test_installation_method(host):
    """Arch installs the package, the others unpack the font in ~/.local/share/fonts."""
    if _os_id(host) == "arch":
        assert host.package("ttf-iosevka-nerd").is_installed
        return
    fonts = host.file("/root/.local/share/fonts/Iosevka")
    assert fonts.is_directory
    assert [name for name in fonts.listdir() if name.endswith(".ttf")]


def test_font_is_known_by_fontconfig(host):
    """fontconfig lists the Iosevka Nerd Font."""
    if _os_id(host) == "arch":
        host.run("fc-cache --force")
    out = host.check_output("fc-list")
    assert "Iosevka" in out
