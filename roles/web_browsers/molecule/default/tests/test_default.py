import re


def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()


def test_packages(host):
    """Chromium and Firefox are installed (Firefox ESR on Debian)."""
    firefox = "firefox-esr" if _os_id(host) == "debian" else "firefox"
    assert host.package("chromium").is_installed
    assert host.package(firefox).is_installed


def test_browsers_run(host):
    """Both browsers report their version."""
    firefox = "firefox-esr" if _os_id(host) == "debian" else "firefox"
    chromium = "chromium-browser" if _os_id(host) == "fedora" else "chromium"
    assert re.search(r"Chromium \d+", host.check_output(f"{chromium} --version"))
    assert re.search(r"Mozilla Firefox \d+", host.check_output(f"{firefox} --version"))
