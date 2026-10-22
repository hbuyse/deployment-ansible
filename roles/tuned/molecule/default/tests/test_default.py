
def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()


def test_tuned_packages(host):
    """TuneD is installed from the package manager, with its power-profiles-daemon replacement on Arch."""
    assert host.package("tuned").is_installed
    if _os_id(host) == "arch":
        assert host.package("tuned-ppd").is_installed


def test_tuned_service(host):
    """The TuneD service is enabled and running."""
    service = host.service("tuned")
    assert service.is_enabled
    assert service.is_running


def test_tuned_ppd_service_on_arch(host):
    """The power-profiles-daemon compatibility service is enabled where the package exists."""
    if _os_id(host) == "fedora":
        return  # the Fedora package of tuned pulls tuned-ppd, which replaces power-profiles-daemon
    if _os_id(host) != "arch":
        assert not host.package("tuned-ppd").is_installed
        return
    assert host.service("tuned-ppd").is_enabled


def test_tuned_answers(host):
    """tuned-adm lists the available profiles."""
    cmd = host.run("tuned-adm list")
    assert cmd.rc == 0, cmd.stderr
    assert "balanced" in cmd.stdout
