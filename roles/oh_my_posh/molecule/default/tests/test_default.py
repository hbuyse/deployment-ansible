from pathlib import Path

ROLE_DIR = Path(__file__).resolve().parents[3]


def test_oh_my_posh_runs(host):
    """oh-my-posh reports its version."""
    cmd = host.run("/root/.local/bin/oh-my-posh version")
    assert cmd.rc == 0, cmd.stderr
    assert cmd.stdout.strip()[0].isdigit()


def test_oh_my_posh_binary(host):
    """The binary is in ~/.local/bin and is executable."""
    binary = host.file("/root/.local/bin/oh-my-posh")
    assert binary.is_file
    assert oct(binary.mode) == "0o755"


def test_configuration(host):
    """The theme of the role is deployed in ~/.config/oh-my-posh."""
    config = host.file("/root/.config/oh-my-posh/config.omp.yaml")
    assert config.is_file
    assert oct(config.mode) == "0o644"
    assert config.content_string == (ROLE_DIR / "files" / "config.omp.yaml").read_text()
