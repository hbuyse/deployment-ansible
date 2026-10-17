import re


def test_repository(host):
    """The VSCodium apt repository is configured with its signing key."""
    source = host.file("/etc/apt/sources.list.d/vscodium.sources")
    assert source.is_file
    assert "URIs: https://paulcarroty.gitlab.io/vscodium-deb-rpm-repo/debs/" in source.content_string
    assert "Suites: vscodium" in source.content_string
    assert "Signed-By:" in source.content_string


def test_vscodium_package(host):
    """VSCodium is installed from that repository."""
    assert host.package("codium").is_installed
    assert "paulcarroty.gitlab.io" in host.check_output("apt-cache policy codium")


def test_vscodium_runs(host):
    """codium reports its version (root needs --no-sandbox and a data directory)."""
    cmd = host.run("codium --version --no-sandbox --user-data-dir /tmp/vscodium-data")
    assert cmd.rc == 0, cmd.stderr
    assert re.match(r"\d+\.\d+\.\d+", cmd.stdout.splitlines()[0])
