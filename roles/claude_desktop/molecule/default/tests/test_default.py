import re

SOURCES_DIR = "/etc/apt/sources.list.d"
KEY = "/usr/share/keyrings/claude-desktop-archive-keyring.asc"


def test_signing_key(host):
    """Anthropic's signing key is installed where the claude-desktop package expects it."""
    key = host.file(KEY)
    assert key.is_file
    assert oct(key.mode) == "0o644"
    assert "BEGIN PGP PUBLIC KEY BLOCK" in key.content_string


def test_apt_repository(host):
    """The apt repository is registered once, with the signing key."""
    source = host.file(f"{SOURCES_DIR}/claude-desktop.list")
    assert source.is_file
    assert f"signed-by={KEY}" in source.content_string
    assert "https://downloads.claude.ai/claude-desktop/apt/stable stable main" in source.content_string

    registered = host.check_output(f"grep -l 'claude-desktop/apt' {SOURCES_DIR}/* || true").split()
    assert registered == [f"{SOURCES_DIR}/claude-desktop.list"], "the package registered the repository a second time"


def test_package_comes_from_the_repository(host):
    """claude-desktop is installed from the Anthropic repository."""
    assert host.package("claude-desktop").is_installed
    assert "downloads.claude.ai" in host.check_output("apt-cache policy claude-desktop")


def test_executable_is_installed(host):
    """The package provides the claude-desktop command."""
    assert host.exists("claude-desktop")


def test_user_can_use_kvm(host):
    """The user is member of the kvm group, needed by the Cowork tab."""
    assert "kvm" in host.user("root").groups


def test_package_version(host):
    """The package has a regular version number."""
    assert re.match(r"\d+\.", host.package("claude-desktop").version)
