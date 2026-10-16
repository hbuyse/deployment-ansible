def test_thunderbird_packages(host):
    """Thunderbird and its English and French dictionaries are installed."""
    for name in ("thunderbird", "thunderbird-i18n-en-us", "thunderbird-i18n-fr"):
        assert host.package(name).is_installed, name


def test_thunderbird_binary(host):
    """The thunderbird command is installed."""
    assert host.exists("thunderbird")
