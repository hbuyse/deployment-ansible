

def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()


def test_shellcheck_runs(host):
    """shellcheck reports its version."""
    cmd = host.run("PATH=/root/.local/bin:$PATH shellcheck --version")
    assert cmd.rc == 0, cmd.stderr
    assert "version:" in cmd.stdout


def test_shellcheck_reports_unquoted_variable(host):
    """shellcheck reports SC2086 for an unquoted variable."""
    cmd = host.run("printf '#!/bin/sh\\necho $a\\n' | PATH=/root/.local/bin:$PATH shellcheck -")
    assert cmd.rc != 0
    assert "SC2086" in cmd.stdout


def test_installation_method(host):
    """Arch and Fedora install the package, the others download the binary in ~/.local/bin."""
    os_id = _os_id(host)
    if os_id == "arch":
        assert host.package("shellcheck").is_installed
    elif os_id == "fedora":
        assert host.package("ShellCheck").is_installed
    else:
        binary = host.file("/root/.local/bin/shellcheck")
        assert binary.is_file
        assert oct(binary.mode) == "0o755"
