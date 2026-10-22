import re

import pytest

RUSTUP_ENV = "PATH=$HOME/.cargo/bin:$PATH RUSTUP_HOME=$HOME/.rustup CARGO_HOME=$HOME/.cargo"


def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()


def _run(host, command):
    return host.run(f"{RUSTUP_ENV} {command}")


@pytest.mark.parametrize("binary", ["rustup", "cargo", "rustc"])
def test_cargo_bin_is_installed(host, binary):
    """rustup, cargo and rustc are installed under ~/.cargo/bin."""
    path = host.file(f"{host.user().home}/.cargo/bin/{binary}")
    assert path.exists
    assert path.mode & 0o111, f"{binary} should be executable"


def test_installer_is_downloaded(host):
    """The rustup installer script is kept in rustup_tmp_dir and is executable."""
    installer = host.file("/tmp/sh.rustup.rs")
    assert installer.is_file
    assert oct(installer.mode) == "0o755"


def test_default_toolchain_is_stable(host):
    """`rustup default` reports the toolchain set by rustup_default_version."""
    cmd = _run(host, "rustup default")
    assert cmd.rc == 0, cmd.stderr
    assert cmd.stdout.startswith("stable-")


def test_toolchain_is_installed(host):
    """The stable toolchain directory exists in ~/.rustup."""
    toolchains = host.file(f"{host.user().home}/.rustup/toolchains")
    assert toolchains.is_directory
    assert any(name.startswith("stable-") for name in toolchains.listdir())


def test_rustc_runs(host):
    """rustc and cargo run and report a semantic version."""
    rustc = _run(host, "rustc --version")
    assert rustc.rc == 0, rustc.stderr
    assert re.match(r"rustc \d+\.\d+\.\d+", rustc.stdout)

    cargo = _run(host, "cargo --version")
    assert cargo.rc == 0, cargo.stderr
    assert re.match(r"cargo \d+\.\d+\.\d+", cargo.stdout)


def test_os_dependencies_are_installed(host):
    """The OS specific build dependencies from vars/<os_family>.yml are installed."""
    expected = {"debian": "libssl-dev", "ubuntu": "libssl-dev", "arch": "openssl", "fedora": "openssl-devel"}
    assert host.package(expected[_os_id(host)]).is_installed


def test_curl_is_installed(host):
    """curl is needed to fetch the installer."""
    assert host.package("curl").is_installed
