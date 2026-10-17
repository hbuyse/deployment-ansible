from pathlib import Path

ROLE_DIR = Path(__file__).resolve().parents[3]
PLUGINS = "/root/.config/tmux/plugins"


def test_tmux_runs(host):
    """tmux is installed and reports its version."""
    cmd = host.run("tmux -V")
    assert cmd.rc == 0, cmd.stderr
    assert cmd.stdout.startswith("tmux ")


def test_configuration(host):
    """The tmux.conf of the role is deployed in ~/.config/tmux."""
    config = host.file("/root/.config/tmux/tmux.conf")
    assert config.is_file
    assert oct(config.mode) == "0o644"
    assert config.content_string == (ROLE_DIR / "files" / "tmux.conf").read_text()


def test_plugins_are_cloned(host):
    """The four plugins are cloned in the plugins directory."""
    for plugin in ("tpm", "tmux", "tmux-sensible", "tmux-yank"):
        assert host.file(f"{PLUGINS}/{plugin}/.git").is_directory, plugin


def test_plugins_are_pinned(host):
    """tpm and the Catppuccin theme are checked out at the version of the role."""
    assert host.check_output(f"git -C {PLUGINS}/tpm describe --tags") == "v3.1.0"
    assert host.check_output(f"git -C {PLUGINS}/tmux describe --tags") == "v1.0.2"


def test_tmux_loads_the_configuration(host):
    """tmux starts a server with the configuration of the role and no error."""
    cmd = host.run("tmux -f /root/.config/tmux/tmux.conf start-server \\; show-options -g default-terminal")
    assert cmd.rc == 0, cmd.stderr
    assert "xterm-256color" in cmd.stdout
