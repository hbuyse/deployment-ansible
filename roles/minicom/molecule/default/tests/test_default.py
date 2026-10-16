import re


def _group(host):
    return "uucp" if host.check_output(". /etc/os-release && echo $ID").strip() == "arch" else "dialout"


def test_minicom_package(host):
    """minicom is installed from the package manager."""
    assert host.package("minicom").is_installed


def test_minicom_runs(host):
    """minicom reports its version."""
    # minicom exits with 1 after printing its version on some builds: only check what it prints
    cmd = host.run("minicom --version")
    assert re.search(r"minicom version \d+\.\d+", cmd.stdout + cmd.stderr)


def test_user_can_open_serial_ports(host):
    """The user is member of the group owning the serial devices (dialout, uucp on Arch)."""
    assert _group(host) in host.user("root").groups


def test_default_configuration(host):
    """~/.minirc.dfl is rendered for the user, with no leftover Jinja."""
    config = host.file("/root/.minirc.dfl")
    assert config.is_file
    assert oct(config.mode) == "0o644"
    content = config.content_string
    assert "{{" not in content
    assert re.search(r"^pu downdir\s+/root/Downloads$", content, flags=re.MULTILINE)
    assert re.search(r"^pu baudrate\s+115200$", content, flags=re.MULTILINE)
