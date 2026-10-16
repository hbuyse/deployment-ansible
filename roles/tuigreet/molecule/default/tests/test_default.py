from pathlib import Path

ROLE_DIR = Path(__file__).resolve().parents[3]


def test_tuigreet_package(host):
    """tuigreet is installed from the package manager."""
    assert host.package("greetd-tuigreet").is_installed
    assert host.exists("tuigreet")


def test_greetd_configuration(host):
    """The configuration of the role is deployed in /etc/greetd."""
    config = host.file("/etc/greetd/config.toml")
    assert config.is_file
    assert oct(config.mode) == "0o644"
    assert config.content_string == (ROLE_DIR / "files" / "config.toml").read_text()
