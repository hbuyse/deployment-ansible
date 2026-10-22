import re

import pytest

THEMES = "/root/.config/foot/themes"


def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()


def _version(host):
    out = host.check_output("foot --version")
    return tuple(int(part) for part in re.search(r"(\d+)\.(\d+)\.(\d+)", out).groups())


def test_foot_packages(host):
    """foot and its terminfo are installed from the package manager."""
    assert host.package("foot").is_installed
    assert host.package("foot-terminfo").is_installed


def test_foot_runs(host):
    """foot reports its version."""
    assert re.search(r"\d+\.\d+\.\d+", host.check_output("foot --version"))


def test_terminal_alternative(host):
    """On Debian family and Fedora, foot is a choice of x-terminal-emulator."""
    os_id = _os_id(host)
    if os_id == "arch":
        pytest.skip("Alternatives are only managed on Debian and Red Hat families")
    tool = "alternatives --display" if os_id == "fedora" else "update-alternatives --query"
    query = host.check_output(f"{tool} x-terminal-emulator")
    assert "/usr/bin/foot" in query


def test_configuration_is_rendered(host):
    """foot.ini is generated from its template, with no leftover Jinja."""
    config = host.file("/root/.config/foot/foot.ini")
    assert config.is_file
    assert oct(config.mode) == "0o644"
    assert "{{" not in config.content_string
    assert "{%" not in config.content_string


@pytest.mark.parametrize("flavour", ["mocha", "macchiato", "frappe"])
def test_catppuccin_themes(host, flavour):
    """The three Catppuccin themes are downloaded."""
    theme = host.file(f"{THEMES}/catppuccin-{flavour}.ini")
    assert theme.is_file
    assert "[colors" in theme.content_string


@pytest.mark.parametrize("flavour", ["mocha", "macchiato", "frappe"])
def test_search_box_options_are_commented_for_old_foot(host, flavour):
    """Before foot 1.13, the options it does not know are commented out of the themes."""
    if _version(host) >= (1, 13, 0):
        pytest.skip("foot knows the options")
    content = host.file(f"{THEMES}/catppuccin-{flavour}.ini").content_string
    assert not re.search(r"^search-box-(no-)?match", content, flags=re.MULTILINE)
