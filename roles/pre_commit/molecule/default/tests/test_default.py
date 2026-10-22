import re


def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()


def test_pre_commit_runs(host):
    """pre-commit reports its version, from the package (Arch, Fedora) or from pipx (Debian family)."""
    cmd = host.run("PATH=/root/.local/bin:$PATH pre-commit --version")
    assert cmd.rc == 0, cmd.stderr
    assert re.fullmatch(r"pre-commit \d+\.\d+\.\d+", cmd.stdout.strip())


def test_installation_method(host):
    """Arch and Fedora use the package, the others pipx."""
    if _os_id(host) in ("arch", "fedora"):
        assert host.package("pre-commit").is_installed
    else:
        assert host.file("/root/.local/bin/pre-commit").exists
