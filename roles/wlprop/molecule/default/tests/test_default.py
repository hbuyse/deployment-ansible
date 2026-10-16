import stat


def test_wlprop_script_installed(host):
    """wlprop script is downloaded to ~/.local/bin/wlprop."""
    script = host.file("/root/.local/bin/wlprop")
    assert script.exists
    assert script.is_file


def test_wlprop_script_executable(host):
    """wlprop script has the executable bit set with the expected mode."""
    script = host.file("/root/.local/bin/wlprop")
    assert stat.S_IXUSR & script.mode
    assert oct(script.mode & 0o777) == "0o755"


def test_wlprop_script_not_empty(host):
    """Downloaded script has actual content."""
    script = host.file("/root/.local/bin/wlprop")
    assert script.size > 0
