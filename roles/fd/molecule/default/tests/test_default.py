import re


def test_fd_package(host):
    """fd is installed from the package manager."""
    assert host.package("fd").is_installed


def test_fd_runs(host):
    """fd reports its version."""
    cmd = host.run("fd --version")
    assert cmd.rc == 0, cmd.stderr
    assert re.fullmatch(r"fd \d+\.\d+\.\d+", cmd.stdout.strip())


def test_fd_finds_files(host):
    """fd finds a file by name."""
    host.run("mkdir -p /tmp/fdtest && touch /tmp/fdtest/needle.txt /tmp/fdtest/other.md")
    assert host.check_output("fd needle /tmp/fdtest").strip() == "/tmp/fdtest/needle.txt"
