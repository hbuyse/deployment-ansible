import re


def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()


def test_ruff_runs(host):
    """ruff reports its version, from the package (Arch) or from pipx (Debian family)."""
    cmd = host.run("PATH=/root/.local/bin:$PATH ruff --version")
    assert cmd.rc == 0, cmd.stderr
    assert re.fullmatch(r"ruff \d+\.\d+\.\d+", cmd.stdout.strip())


def test_ruff_finds_an_unused_import(host):
    """ruff reports the unused import F401."""
    host.run("printf 'import os\\n' > /tmp/unused.py")
    cmd = host.run("PATH=/root/.local/bin:$PATH ruff check --select F401 --no-cache /tmp/unused.py")
    assert cmd.rc != 0
    assert "F401" in cmd.stdout


def test_installation_method(host):
    """Arch uses the package, the others pipx."""
    if _os_id(host) == "arch":
        assert host.package("ruff").is_installed
    else:
        assert host.file("/root/.local/bin/ruff").exists
