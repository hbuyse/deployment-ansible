

def test_commands_are_installed(host):
    """The language server commands are in the PATH, installed with npm or from the Arch package."""
    for name in ("ansible-language-server",):
        assert host.exists(name), name
