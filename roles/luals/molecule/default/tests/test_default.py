

def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()


def test_luals_runs(host):
    """lua-language-server reports its version."""
    cmd = host.run("PATH=/opt/luals/bin:$PATH lua-language-server --version")
    assert cmd.rc == 0, cmd.stderr
    assert cmd.stdout.strip()[0].isdigit()


def test_installation_method(host):
    """Arch installs the package, the others unpack the release in /opt/luals."""
    if _os_id(host) == "arch":
        assert host.package("lua-language-server").is_installed
    else:
        executable = host.file("/opt/luals/bin/lua-language-server")
        assert executable.is_file
        assert executable.mode & 0o111
