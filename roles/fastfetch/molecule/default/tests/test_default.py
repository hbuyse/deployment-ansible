

def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()
import re


def test_fastfetch_runs(host):
    """fastfetch reports its version."""
    cmd = host.run("PATH=/root/.local/bin:$PATH fastfetch --version")
    assert cmd.rc == 0, cmd.stderr
    assert re.search(r"fastfetch \d+\.\d+\.\d+", cmd.stdout)


def test_installation_method(host):
    """Arch installs the package, the others unpack the release in ~/.local."""
    if _os_id(host) == "arch":
        assert host.package("fastfetch").is_installed
    else:
        assert host.file("/root/.local/bin/fastfetch").is_file


def test_configuration_is_rendered(host):
    """The configuration is generated from its template, with no leftover Jinja, and fastfetch accepts it."""
    config = host.file("/root/.config/fastfetch/config.jsonc")
    assert config.is_file
    assert oct(config.mode) == "0o644"
    assert "{{" not in config.content_string
    cmd = host.run("PATH=/root/.local/bin:$PATH fastfetch --config /root/.config/fastfetch/config.jsonc --pipe")
    assert cmd.rc == 0, cmd.stderr
