def test_greetd_package(host):
    """greetd is installed from the package manager."""
    assert host.package("greetd").is_installed
    assert host.exists("greetd")


def test_greetd_service_is_enabled(host):
    """The greetd service is enabled (it is not started: it would take over the console)."""
    assert host.service("greetd").is_enabled


def test_default_configuration(host):
    """The package provides the configuration read by greetd."""
    assert host.file("/etc/greetd/config.toml").is_file
