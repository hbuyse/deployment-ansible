
def _package(host):
    os_id = host.check_output(". /etc/os-release && echo $ID").strip()
    return "python-isort" if os_id == "arch" else "isort"


def test_isort_package(host):
    """isort is installed from the package manager."""
    assert host.package(_package(host)).is_installed


def test_isort_runs(host):
    """isort reports its version."""
    cmd = host.run("isort --version")
    assert cmd.rc == 0, cmd.stderr
    assert "VERSION" in cmd.stdout


def test_isort_sorts_imports(host):
    """isort puts the imports in alphabetical order."""
    cmd = host.run("printf 'import sys\\nimport os\\n' | isort -")
    assert cmd.rc == 0, cmd.stderr
    assert cmd.stdout.split() == ["import", "os", "import", "sys"]
