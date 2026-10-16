import re

import pytest

HOME = "/root"


def _is_debian_family(host):
    return host.check_output(". /etc/os-release && echo $ID").strip() in ("debian", "ubuntu")


def _claude(host):
    return host.run(f"PATH={HOME}/.local/bin:$PATH claude --version")


def test_claude_runs(host):
    """claude is installed and reports its version."""
    cmd = _claude(host)
    assert cmd.rc == 0, cmd.stderr
    assert re.search(r"\d+\.\d+\.\d+ \(Claude Code\)", cmd.stdout)


def test_apt_repository(host):
    """On Debian family, the Anthropic apt repository of the requested channel is configured."""
    if not _is_debian_family(host):
        pytest.skip("Only Debian family uses the apt repository")
    source = host.file("/etc/apt/sources.list.d/claude-code.sources")
    assert source.is_file
    assert "URIs: https://downloads.claude.ai/claude-code/apt/stable" in source.content_string
    assert "Suites: stable" in source.content_string
    assert "Signed-By:" in source.content_string


def test_package_comes_from_the_repository(host):
    """On Debian family, claude-code is the package of the Anthropic repository, installed in /usr/bin."""
    if not _is_debian_family(host):
        pytest.skip("Only Debian family uses the apt repository")
    assert host.package("claude-code").is_installed
    assert "downloads.claude.ai" in host.check_output("apt-cache policy claude-code")
    assert host.file("/usr/bin/claude").exists


def test_native_installation(host):
    """Elsewhere, the native installer links claude in ~/.local/bin and does not leave its script behind."""
    if _is_debian_family(host):
        pytest.skip("Debian family uses the package")
    assert host.file(f"{HOME}/.local/bin/claude").exists
    assert not host.file("/tmp/claude-code-install.sh").exists
