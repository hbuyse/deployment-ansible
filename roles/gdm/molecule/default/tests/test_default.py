def test_gdm_packages(host):
    """GDM and Xwayland are installed."""
    assert host.package("gdm").is_installed
    assert host.package("xorg-xwayland").is_installed


def test_gdm_binary(host):
    """The gdm command is installed."""
    assert host.exists("gdm")
