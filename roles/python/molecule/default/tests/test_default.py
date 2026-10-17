import re


def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()


def test_python_packages(host):
    """Python and virtualenv are installed from the package manager."""
    if _os_id(host) == "arch":
        names = ["python", "python-virtualenv"]
    else:
        names = ["python3", "python3-venv", "python3-virtualenv", "virtualenvwrapper"]
    for name in names:
        assert host.package(name).is_installed, name


def test_python_runs(host):
    """python3 reports a Python 3 version."""
    cmd = host.run("python3 --version")
    assert cmd.rc == 0, cmd.stderr
    assert re.fullmatch(r"Python 3\.\d+\.\d+", cmd.stdout.strip())


def test_virtualenv_creates_an_environment(host):
    """virtualenv creates a working environment."""
    assert host.run("virtualenv /tmp/venv").rc == 0
    assert host.run("/tmp/venv/bin/python --version").rc == 0


def test_virtualenvwrapper_on_debian_family(host):
    """Debian family installs virtualenvwrapper from its package."""
    if _os_id(host) == "arch":
        return
    assert host.file("/usr/share/virtualenvwrapper/virtualenvwrapper.sh").exists
