import re


def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()


def test_shfmt_runs(host):
    """shfmt reports its version."""
    cmd = host.run("PATH=/root/.local/bin:$PATH shfmt --version")
    assert cmd.rc == 0, cmd.stderr
    if _os_id(host) == "fedora":
        return  # the Fedora package is built without a version number
    assert re.fullmatch(r"v?\d+\.\d+\.\d+", cmd.stdout.strip())


def test_shfmt_formats_shell(host):
    """shfmt indents the body of a condition with a tab."""
    cmd = host.run("printf 'if true;then\necho a\nfi\n' | PATH=/root/.local/bin:$PATH shfmt")
    assert cmd.rc == 0, cmd.stderr
    assert cmd.stdout.splitlines() == ["if true; then", "\techo a", "fi"]


def test_installation_method(host):
    """The package is installed everywhere, Ubuntu also downloads the binary because it forces the source install."""
    assert host.package("shfmt").is_installed
    if _os_id(host) == "ubuntu":
        binary = host.file("/root/.local/bin/shfmt")
        assert binary.is_file
        assert oct(binary.mode) == "0o755"
