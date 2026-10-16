import re


def test_brightnessctl_package(host):
    """brightnessctl is installed from the package manager."""
    assert host.package("brightnessctl").is_installed


def test_brightnessctl_runs(host):
    """brightnessctl reports its version."""
    cmd = host.run("brightnessctl --version")
    assert cmd.rc == 0, cmd.stderr
    assert re.search(r"\d+\.\d+", cmd.stdout + cmd.stderr)


def test_user_is_in_video_group(host):
    """The user belongs to the group allowed to write the backlight, so that sudo is not needed."""
    assert "video" in host.user("root").groups
