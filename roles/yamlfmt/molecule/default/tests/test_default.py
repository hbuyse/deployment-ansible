import re


def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()


def test_yamlfmt_runs(host):
    """yamlfmt reports its version."""
    cmd = host.run("PATH=/root/.local/bin:$PATH yamlfmt -version")
    assert cmd.rc == 0, cmd.stderr
    # The Arch package prints "yamlfmt (devel)"
    assert re.search(r"v?\d+\.\d+\.\d+|\(devel\)", cmd.stdout + cmd.stderr)


def test_yamlfmt_formats_yaml(host):
    """yamlfmt removes the extra spaces."""
    cmd = host.run("printf 'a:    1\\n' | PATH=/root/.local/bin:$PATH yamlfmt -in")
    assert cmd.rc == 0, cmd.stderr
    assert cmd.stdout.strip() == "a: 1"


def test_installation_method(host):
    """Arch installs the package, the others download the binary in ~/.local/bin."""
    if _os_id(host) == "arch":
        assert host.package("yamlfmt").is_installed
    else:
        binary = host.file("/root/.local/bin/yamlfmt")
        assert binary.is_file
        assert oct(binary.mode) == "0o755"
