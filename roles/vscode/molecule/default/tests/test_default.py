import re


def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()


def test_repository_on_debian_family(host):
    """Debian family uses the Microsoft apt repository."""
    if _os_id(host) not in ("debian", "ubuntu"):
        return
    source = host.file("/etc/apt/sources.list.d/vscode.sources")
    assert source.is_file
    assert "URIs: https://packages.microsoft.com/repos/code" in source.content_string
    assert "Suites: stable" in source.content_string
    assert "microsoft.com" in host.check_output("apt-cache policy code")


def test_repository_on_fedora(host):
    """Fedora uses the Microsoft yum repository."""
    if _os_id(host) != "fedora":
        return
    repository = host.file("/etc/yum.repos.d/vscode.repo")
    assert repository.is_file
    assert "baseurl = https://packages.microsoft.com/yumrepos/vscode" in repository.content_string
    assert "gpgcheck = 1" in repository.content_string


def test_vscode_package(host):
    """Visual Studio Code is installed."""
    assert host.package("code").is_installed


def test_vscode_runs(host):
    """code reports its version (root needs --no-sandbox and a data directory)."""
    cmd = host.run("code --version --no-sandbox --user-data-dir /tmp/vscode-data")
    assert cmd.rc == 0, cmd.stderr
    assert re.match(r"\d+\.\d+\.\d+", cmd.stdout.splitlines()[0])
