import re


def test_podman_package(host):
    """podman is installed from the package manager."""
    assert host.package("podman").is_installed


def test_podman_runs(host):
    """podman reports its version."""
    cmd = host.run("podman --version")
    assert cmd.rc == 0, cmd.stderr
    assert re.fullmatch(r"podman version \d+\.\d+\.\d+.*", cmd.stdout.strip())
