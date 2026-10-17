def test_zoom_package(host):
    """The Zoom client is installed from the downloaded package."""
    assert host.package("zoom").is_installed


def test_zoom_executable(host):
    """The Zoom executable is installed."""
    assert host.file("/opt/zoom/zoom").is_file
