import re


def test_packages(host):
    """Chromium and Firefox are installed."""
    assert host.package("chromium").is_installed
    assert host.package("firefox").is_installed


def test_browsers_run(host):
    """Both browsers report their version."""
    assert re.search(r"Chromium \d+", host.check_output("chromium --version"))
    assert re.search(r"Mozilla Firefox \d+", host.check_output("firefox --version"))
