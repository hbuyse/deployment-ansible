import re


def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()


def test_yq_runs(host):
    """yq reports its version."""
    cmd = host.run("PATH=/root/.local/bin:$PATH yq --version")
    assert cmd.rc == 0, cmd.stderr
    assert re.search(r"yq .*version v?\d+\.\d+\.\d+", cmd.stdout)


def test_yq_reads_yaml(host):
    """yq extracts a nested value from a YAML document."""
    cmd = host.run("echo 'a: {b: 3}' | PATH=/root/.local/bin:$PATH yq '.a.b'")
    assert cmd.rc == 0, cmd.stderr
    assert cmd.stdout.strip() == "3"


def test_installation_method(host):
    """Arch installs go-yq, the others download the binary in ~/.local/bin and its man page."""
    if _os_id(host) == "arch":
        assert host.package("go-yq").is_installed
        return
    binary = host.file("/root/.local/bin/yq")
    assert binary.is_file
    assert oct(binary.mode) == "0o755"
    assert host.file("/root/.local/share/man/man1/yq.1").is_file
