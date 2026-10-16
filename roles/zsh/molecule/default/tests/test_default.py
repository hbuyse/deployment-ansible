import re

import pytest

HOME = "/root"
OMZ = f"{HOME}/.oh-my-zsh"
OMZ_CUSTOM = f"{OMZ}/custom"

CUSTOM_PLUGINS = [
    "zsh-autosuggestions",
    "zsh-completions",
    "zsh-history-substring-search",
    "zsh-syntax-highlighting",
    "you-should-use",
]


def test_zsh_is_installed(host):
    """zsh is installed where the role expects it."""
    assert host.file("/usr/bin/zsh").exists
    assert host.run("/usr/bin/zsh --version").rc == 0


def test_zsh_is_the_login_shell(host):
    """The user's login shell is /usr/bin/zsh."""
    assert host.user("root").shell == "/usr/bin/zsh"


def test_login_shell_is_a_valid_shell(host):
    """The login shell is listed in /etc/shells, otherwise some services refuse the login."""
    shells = host.file("/etc/shells").content_string.splitlines()
    assert "/usr/bin/zsh" in shells


def test_oh_my_zsh_is_a_git_checkout(host):
    """oh-my-zsh is cloned from upstream."""
    assert host.file(f"{OMZ}/oh-my-zsh.sh").is_file
    assert host.file(f"{OMZ}/.git").is_directory


@pytest.mark.parametrize("plugin", CUSTOM_PLUGINS)
def test_custom_plugins_are_cloned(host, plugin):
    """Each custom plugin is cloned in the oh-my-zsh custom directory."""
    assert host.file(f"{OMZ_CUSTOM}/plugins/{plugin}/.git").is_directory


def test_powerlevel10k_theme_is_cloned(host):
    """The powerlevel10k theme is cloned in the oh-my-zsh custom directory."""
    assert host.file(f"{OMZ_CUSTOM}/themes/powerlevel10k/powerlevel10k.zsh-theme").is_file


@pytest.mark.parametrize("name", [".zshrc", ".p10k.zsh", ".xprofile", ".Xresources", ".zprofile"])
def test_configuration_files(host, name):
    """The configuration files are deployed with mode 0644."""
    config = host.file(f"{HOME}/{name}")
    assert config.is_file
    assert oct(config.mode) == "0o644"


@pytest.mark.parametrize("name", [".zshrc", ".p10k.zsh", ".zprofile"])
def test_zsh_configuration_has_no_syntax_error(host, name):
    """zsh can parse the shell configuration files."""
    cmd = host.run(f"/usr/bin/zsh -n {HOME}/{name}")
    assert cmd.rc == 0, cmd.stderr


def test_zprofile_is_rendered(host):
    """The zprofile template has no leftover Jinja and keeps the Linux specific part."""
    content = host.file(f"{HOME}/.zprofile").content_string
    assert "{{" not in content
    assert "{%" not in content
    assert "DOCKER_SOCKET" in content


def test_zprofile_does_not_contain_machine_specific_blocks(host):
    """Blocks reserved to hbuyse-promax14 are not rendered on another host."""
    content = host.file(f"{HOME}/.zprofile").content_string
    assert "arcanist" not in content
    assert "PERL5_LIB" not in content


def test_zshrc_plugins_exist(host):
    """Every plugin enabled in .zshrc is available in oh-my-zsh or in the custom directory."""
    zshrc = host.file(f"{HOME}/.zshrc").content_string
    plugins = re.findall(r"^plugins\+=\(([^)\s]+)\)", zshrc, flags=re.MULTILINE)
    assert plugins, "no plugin found in .zshrc"
    missing = [
        plugin
        for plugin in plugins
        if not host.file(f"{OMZ}/plugins/{plugin}").is_directory
        and not host.file(f"{OMZ_CUSTOM}/plugins/{plugin}").is_directory
    ]
    assert not missing, f"plugins enabled in .zshrc but not installed: {missing}"


def test_dependency_roles_were_applied(host):
    """The roles listed in meta/main.yml installed their tools."""
    for command in ("tmux", "fzf", "direnv", "fastfetch"):
        found = host.run(f"PATH=$PATH:{HOME}/.local/bin command -v {command}")
        assert found.rc == 0, f"{command} is not installed"
