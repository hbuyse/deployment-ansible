

def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()
import re


def test_pipx_runs(host):
    """pipx reports its version."""
    cmd = host.run("PATH=/root/.local/bin:$PATH pipx --version")
    assert cmd.rc == 0, cmd.stderr
    assert re.fullmatch(r"\d+\.\d+(\.\d+)*", cmd.stdout.strip())


def test_installation_method(host):
    """Arch installs the package, the others install pipx in the user space."""
    if _os_id(host) == "arch":
        assert host.package("python-pipx").is_installed
    else:
        assert host.file("/root/.local/bin/pipx").exists


def test_temporary_virtualenv_is_removed(host):
    """The handler removes the temporary virtualenv used for the bootstrap."""
    assert host.check_output("ls -d /tmp/*pipx* 2>/dev/null || true") == ""
