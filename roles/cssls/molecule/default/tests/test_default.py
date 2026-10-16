import re

import pytest


def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()


def test_commands_are_installed(host):
    """The language server commands are in the PATH, installed with npm or from the Arch package."""
    for name in ("vscode-css-language-server",):
        assert host.exists(name), name


def test_package_on_arch(host):
    """Arch installs the language server from its own package instead of npm."""
    if _os_id(host) != "arch":
        pytest.skip("Only Arch has a package for it")
    assert host.package("vscode-css-languageserver").is_installed
