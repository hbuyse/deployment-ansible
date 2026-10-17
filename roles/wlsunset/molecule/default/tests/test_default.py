UNIT = "/root/.config/systemd/user/wlsunset.service"
SYSTEMCTL = "XDG_RUNTIME_DIR=/run/user/0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/0/bus systemctl --user"


def test_wlsunset_package(host):
    """wlsunset is installed from the package manager."""
    assert host.package("wlsunset").is_installed
    assert host.exists("wlsunset")


def test_unit_file_is_rendered(host):
    """The unit file of the user service is generated with the coordinates of the configuration."""
    unit = host.file(UNIT)
    assert unit.is_file
    assert oct(unit.mode) == "0o644"
    content = unit.content_string
    assert "{{" not in content
    assert "-l 48.86 -L 2.33" in content


def test_exec_start_has_every_option(host):
    """systemd reads the temperatures and the duration as arguments of the command."""
    cmd = host.run(f"{SYSTEMCTL} show wlsunset --property=ExecStart --value")
    assert cmd.rc == 0, cmd.stderr
    for option in ("-l 48.86", "-L 2.33", "-t 4000", "-T 6500", "-d 900"):
        assert option in cmd.stdout, option


def test_service_is_enabled(host):
    """The 'Restart wlsunset service' handler enabled the user service."""
    cmd = host.run(f"{SYSTEMCTL} is-enabled wlsunset")
    assert cmd.stdout.strip() == "enabled", cmd.stderr
