import re


def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()


def test_ansible_lint_runs(host):
    """ansible-lint reports its version, from the package (Arch) or from pipx (Debian family)."""
    cmd = host.run("PATH=/root/.local/bin:$PATH ansible-lint --version")
    assert cmd.rc == 0, cmd.stderr
    assert re.search(r"ansible-lint \d+\.\d+", cmd.stdout)


def test_installation_method(host):
    """Arch uses the package, the others pipx."""
    if _os_id(host) == "arch":
        assert host.package("ansible-lint").is_installed
    else:
        assert host.file("/root/.local/bin/ansible-lint").exists
