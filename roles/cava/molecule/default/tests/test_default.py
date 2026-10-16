from pathlib import Path

ROLE_DIR = Path(__file__).resolve().parents[3]


def test_cava_package(host):
    """cava is installed from the package manager."""
    assert host.package("cava").is_installed


def test_cava_runs(host):
    """cava reports its version."""
    cmd = host.run("cava -v")
    assert cmd.rc == 0, cmd.stderr
    assert "cava" in (cmd.stdout + cmd.stderr).lower()


def test_cava_configuration(host):
    """The configuration of the role is deployed in ~/.config/cava."""
    config = host.file("/root/.config/cava/config")
    assert config.is_file
    assert oct(config.mode) == "0o644"
    assert config.content_string == (ROLE_DIR / "files" / "config").read_text()
    assert oct(host.file("/root/.config/cava").mode) == "0o755"
