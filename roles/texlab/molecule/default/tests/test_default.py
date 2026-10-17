

def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()


def test_texlab_runs(host):
    """texlab reports its version."""
    cmd = host.run("PATH=/root/.local/bin:$PATH texlab --version")
    assert cmd.rc == 0, cmd.stderr
    assert cmd.stdout.startswith("texlab ")


def test_installation_method(host):
    """Arch installs the package, the others download the binary in ~/.local/bin."""
    if _os_id(host) == "arch":
        assert host.package("texlab").is_installed
    else:
        binary = host.file("/root/.local/bin/texlab")
        assert binary.is_file
        assert oct(binary.mode) == "0o755"
