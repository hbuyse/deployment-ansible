import re
from pathlib import Path

import pytest
import yaml

ROLE_DIR = Path(__file__).resolve().parents[3]


def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()


def _is_debian_family(host):
    return _os_id(host) in ("debian", "ubuntu")


@pytest.fixture(scope="module")
def expected_major():
    """Major version pinned in vars/debian.yml."""
    variables = yaml.safe_load((ROLE_DIR / "vars" / "debian.yml").read_text())
    return str(variables["nodejs_version"])


def test_node_runs(host):
    """node is installed and reports a version."""
    cmd = host.run("node --version")
    assert cmd.rc == 0, cmd.stderr
    assert re.fullmatch(r"v\d+\.\d+\.\d+", cmd.stdout.strip())


def test_npm_runs(host):
    """npm is installed and reports a version."""
    cmd = host.run("npm --version")
    assert cmd.rc == 0, cmd.stderr
    assert re.fullmatch(r"\d+\.\d+\.\d+", cmd.stdout.strip())


def test_node_major_matches_nodejs_version(host, expected_major):
    """On Debian family, the installed node comes from NodeSource with the requested major version."""
    if not _is_debian_family(host):
        pytest.skip("nodejs_version only applies to the NodeSource repository")
    assert host.check_output("node --version").startswith(f"v{expected_major}.")


def test_nodesource_repository(host):
    """The NodeSource repository is declared for the right major version and architecture."""
    if not _is_debian_family(host):
        pytest.skip("NodeSource is a Debian family repository")
    sources = host.file("/etc/apt/sources.list.d/nodesource.sources")
    assert sources.is_file
    arch = host.check_output("dpkg --print-architecture")
    assert "https://deb.nodesource.com/node_" in sources.content_string
    assert f"Architectures: {arch}" in sources.content_string
    assert "Signed-By:" in sources.content_string


def test_apt_preferences_pin_nodesource(host):
    """The pin makes apt prefer NodeSource over the distribution nodejs package."""
    if not _is_debian_family(host):
        pytest.skip("apt preferences only exist on Debian family")
    pref = host.file("/etc/apt/preferences.d/nodejs.pref")
    assert pref.is_file
    assert oct(pref.mode) == "0o644"
    assert "Pin: origin deb.nodesource.com" in pref.content_string

    policy = host.check_output("apt-cache policy nodejs")
    candidate = re.search(r"Candidate: (\S+)", policy).group(1)
    assert "nodesource" in candidate, f"candidate {candidate} does not come from NodeSource"


def test_nodejs_package_is_installed(host):
    """The nodejs package is installed from the package manager (Fedora names it after the major version)."""
    if _os_id(host) == "fedora":
        assert host.run("rpm -q --whatprovides nodejs").rc == 0
    else:
        assert host.package("nodejs").is_installed


def test_dependencies_are_installed_on_debian(host):
    """The dependencies needed to add the repository are installed."""
    if not _is_debian_family(host):
        pytest.skip("nodejs_dependencies only exists on Debian family")
    for name in ("apt-transport-https", "ca-certificates", "curl", "gnupg"):
        assert host.package(name).is_installed, name
