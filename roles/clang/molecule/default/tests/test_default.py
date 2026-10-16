import re
from pathlib import Path

import pytest
import yaml

ROLE_DIR = Path(__file__).resolve().parents[3]
BIN_DIR = "/usr/bin"


def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()


def _is_debian_family(host):
    return _os_id(host) in ("debian", "ubuntu")


@pytest.fixture(scope="module")
def llvm_versions():
    defaults = yaml.safe_load((ROLE_DIR / "defaults" / "main.yml").read_text())
    return [str(version) for version in defaults["clang_llvm_versions"]]


@pytest.fixture(scope="module")
def latest(llvm_versions):
    return llvm_versions[-1]


@pytest.fixture(scope="module")
def alternatives():
    """{master: [slaves]} as declared in clang_alternatives in vars/debian.yml."""
    variables = yaml.safe_load((ROLE_DIR / "vars" / "debian.yml").read_text())
    return {entry["name"]: entry["subcommands"] for entry in variables["clang_alternatives"]}


@pytest.fixture
def debian_family(host):
    if not _is_debian_family(host):
        pytest.skip("LLVM apt repositories and alternatives only apply to Debian family")


def test_llvm_apt_signing_key(host, debian_family):
    """The LLVM repository signing key is installed."""
    key = host.file("/etc/apt/keyrings/apt.llvm.org.asc")
    assert key.is_file
    assert oct(key.mode) == "0o644"


def test_llvm_apt_repositories(host, debian_family, llvm_versions):
    """One apt source per LLVM version in clang_llvm_versions, all signed with the LLVM key."""
    release = host.check_output(". /etc/os-release && echo $VERSION_CODENAME")
    for version in llvm_versions:
        source = host.file(f"/etc/apt/sources.list.d/llvm-{version}.sources")
        assert source.is_file, f"missing source for LLVM {version}"
        assert f"llvm-toolchain-{release}-{version}" in source.content_string
        assert "Signed-By: /etc/apt/keyrings/apt.llvm.org.asc" in source.content_string


@pytest.mark.parametrize("tool", ["clang", "clangd", "clang-format", "clang-tidy", "lldb", "llvm-config"])
def test_versioned_tools_run(host, debian_family, latest, tool):
    """The tools of the latest LLVM version are installed and report that version."""
    cmd = host.run(f"{BIN_DIR}/{tool}-{latest} --version")
    assert cmd.rc == 0, cmd.stderr
    assert re.search(rf"\b{latest}\.\d+\.\d+", cmd.stdout + cmd.stderr)


def test_alternatives_select_latest(host, debian_family, latest, alternatives):
    """`clang` and `llvm-config` are alternatives whose current choice is the latest LLVM version."""
    for master in alternatives:
        query = host.check_output(f"update-alternatives --query {master}")
        assert f"Value: {BIN_DIR}/{master}-{latest}" in query.splitlines()


def test_alternatives_slaves_point_to_latest(host, debian_family, latest, alternatives):
    """Every subcommand of the alternatives is linked to the latest LLVM version."""
    for master, slaves in alternatives.items():
        query = host.check_output(f"update-alternatives --query {master}")
        lines = [line.strip() for line in query.splitlines()]
        missing = [slave for slave in slaves if f"{slave} {BIN_DIR}/{slave}-{latest}" not in lines]
        assert not missing, f"not linked to LLVM {latest} for {master}: {missing}"


def test_alternatives_have_no_dangling_link(host, debian_family, latest, alternatives):
    """The alternatives module does not check its targets: make sure every link leads to an installed binary."""
    names = [name for master, slaves in alternatives.items() for name in [master, *slaves]]
    dangling = [name for name in names if not host.file(f"{BIN_DIR}/{name}").exists]
    assert not dangling, f"dangling links for LLVM {latest}, remove them from tasks/alternatives.yml: {dangling}"


def test_unversioned_clang_is_latest(host, debian_family, latest):
    """Calling `clang` without a version runs the latest LLVM version."""
    cmd = host.run("clang --version")
    assert cmd.rc == 0, cmd.stderr
    assert re.search(rf"clang version {latest}\.", cmd.stdout)


def test_clang_runs_on_arch(host):
    """On Arch the distribution package provides clang and clangd."""
    if _os_id(host) != "arch":
        pytest.skip("Only for Arch Linux")
    assert host.package("clang").is_installed
    for tool in ("clang", "clangd", "clang-format", "clang-tidy"):
        assert host.run(f"{tool} --version").rc == 0, tool


def test_clangd_configuration(host):
    """The clangd configuration is deployed and is valid YAML."""
    config = host.file("/root/.config/clangd/config.yaml")
    assert config.is_file
    expected = (ROLE_DIR / "files" / "config.yaml").read_text()
    assert config.content_string == expected
    assert yaml.safe_load(config.content_string) is not None
