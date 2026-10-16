def test_podman_package_installed(host):
    """The podman package is installed."""
    assert host.package("podman").is_installed


def test_podman_binary_available(host):
    """The podman binary is on the PATH and reports a version."""
    binary = host.file("/usr/bin/podman")
    assert binary.exists
    assert binary.is_file

    out = host.check_output("podman --version")
    assert "podman version" in out
