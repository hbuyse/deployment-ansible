
def _package(host):
    return "python-black" if host.check_output(". /etc/os-release && echo $ID").strip() == "arch" else "black"


def test_black_package(host):
    """black is installed from the package manager."""
    assert host.package(_package(host)).is_installed


def test_black_runs(host):
    """black reports its version."""
    cmd = host.run("black --version")
    assert cmd.rc == 0, cmd.stderr
    assert cmd.stdout.startswith("black, ")


def test_black_formats_python(host):
    """black rewrites a badly formatted dictionary."""
    cmd = host.run("printf 'x = {  \"a\":1}\\n' | black -q -")
    assert cmd.rc == 0, cmd.stderr
    assert cmd.stdout.strip() == 'x = {"a": 1}'
