import re

import pytest


def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()


def test_docker_repository(host):
    """The Docker apt repository matches the distribution, release and architecture, the yum one on Fedora."""
    distribution = _os_id(host)
    if distribution == "fedora":
        repository = host.file("/etc/yum.repos.d/docker-ce.repo")
        assert repository.is_file
        baseurl = "baseurl = https://download.docker.com/linux/fedora/$releasever/$basearch/stable"
        assert baseurl in repository.content_string
        assert "gpgcheck = 1" in repository.content_string
        return
    release = host.check_output(". /etc/os-release && echo $VERSION_CODENAME")
    arch = host.check_output("dpkg --print-architecture")

    source = host.file("/etc/apt/sources.list.d/docker.sources")
    assert source.is_file
    assert f"URIs: https://download.docker.com/linux/{distribution}" in source.content_string
    assert f"Suites: {release}" in source.content_string
    assert "Components: stable" in source.content_string
    assert f"Architectures: {arch}" in source.content_string
    assert "Signed-By:" in source.content_string


@pytest.mark.parametrize(
    "package",
    ["docker-ce", "docker-ce-cli", "containerd.io", "docker-buildx-plugin", "docker-compose-plugin"],
)
def test_packages_are_installed(host, package):
    """Every package from vars/debian.yml is installed."""
    assert host.package(package).is_installed


def test_packages_come_from_docker_repository(host):
    """docker-ce is installed from download.docker.com and not from the distribution."""
    if _os_id(host) == "fedora":
        assert "docker-ce-stable" in host.check_output("dnf repoquery --installed --qf '%{from_repo}' docker-ce")
        return
    policy = host.check_output("apt-cache policy docker-ce")
    assert "download.docker.com" in policy


def test_docker_cli_and_plugins(host):
    """The docker client and its compose and buildx plugins run."""
    assert re.search(r"Docker version \d+\.\d+\.\d+", host.check_output("docker --version"))
    assert re.search(r"Docker Compose version", host.check_output("docker compose version"))
    assert re.search(r"github.com/docker/buildx", host.check_output("docker buildx version"))


def test_docker_group_exists(host):
    """The docker group is created by the packages."""
    assert host.group("docker").exists


def test_user_is_in_docker_group(host):
    """The user running the role is member of the docker group."""
    assert "docker" in host.user("root").groups


def test_docker_service_is_enabled_and_running(host):
    """The 'Restart docker service' handler leaves docker enabled and running."""
    service = host.service("docker")
    assert service.is_enabled
    assert service.is_running


def test_docker_daemon_answers(host):
    """The docker daemon answers to the client."""
    cmd = host.run("docker version --format '{{.Server.Version}}'")
    assert cmd.rc == 0, cmd.stderr
    assert re.fullmatch(r"\d+\.\d+\.\d+", cmd.stdout.strip())
