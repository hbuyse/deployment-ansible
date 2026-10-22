from pathlib import Path

import yaml

ROLE_DIR = Path(__file__).resolve().parents[3]
PLUGINS = "/root/.config/tmux/plugins"


def _versions():
    """Version of each plugin, as written in the task that clones them (Renovate updates it)."""
    tasks = yaml.safe_load((ROLE_DIR / "tasks" / "main.yml").read_text())
    task = next(task for task in tasks if task.get("name") == "Download TMux plugins manager")
    return {item["plugin_dir"]: item["version"] for item in task["loop"]}


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
    """tpm and the Catppuccin theme are checked out at the version of the role.

    All the tags of the commit are looked at: a floating tag such as v1 points to the same commit as v1.0.3, and
    `git describe` may answer with it.
    """
    versions = _versions()
    for plugin in ("tpm", "tmux"):
        tags = host.check_output(f"git -C {PLUGINS}/{plugin} tag --points-at HEAD").split()
        assert versions[plugin] in tags, f"{plugin}: {versions[plugin]} is not in {tags}"


def test_theme_version_of_tmux_conf_is_the_one_of_the_role():
    """The plugin line of tmux.conf asks for the version that the role clones."""
    line = f"set -g @plugin 'catppuccin/tmux#{_versions()['tmux']}'"
    assert line in (ROLE_DIR / "files" / "tmux.conf").read_text()


def test_tmux_loads_the_configuration(host):
    """tmux starts a server with the configuration of the role and no error."""
    cmd = host.run("tmux -f /root/.config/tmux/tmux.conf start-server \\; show-options -g default-terminal")
    assert cmd.rc == 0, cmd.stderr
    assert "xterm-256color" in cmd.stdout
