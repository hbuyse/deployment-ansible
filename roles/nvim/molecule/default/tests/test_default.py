import pytest


def test_nvim_binary_exists(host):
    """nvim binary is installed and executable."""
    # Check both package manager path and static binary path
    assert host.file("/usr/bin/nvim").exists or host.file("/root/.local/bin/nvim").exists


def test_nvim_version(host):
    """nvim reports a valid version >= 0.10."""
    try:
        out = host.check_output("nvim --version")
    except AssertionError:
        out = host.check_output("/root/.local/bin/nvim --version")

    first_line = out.splitlines()[0]
    assert "NVIM v" in first_line

    version_str = first_line.split("v")[1].split()[0]
    major, minor = map(int, version_str.split(".")[:2])
    assert (major, minor) >= (0, 10)


def test_nvim_config_dir_exists(host):
    """~/.config/nvim directory exists with correct permissions."""
    config_dir = host.file("/root/.config/nvim")
    assert config_dir.is_directory
    assert oct(config_dir.mode) == "0o755"


def test_init_lua_exists(host):
    """Main init.lua file is deployed."""
    init_file = host.file("/root/.config/nvim/init.lua")
    assert init_file.exists
    assert init_file.contains("vim.g.mapleader = ' '")


def test_hbuyse_init_lua_exists(host):
    """Templated lua/hbuyse/init.lua is deployed."""
    init_file = host.file("/root/.config/nvim/lua/hbuyse/init.lua")
    assert init_file.exists
    assert init_file.contains("hbuyse.lazy_config")


def test_formatter_lua_exists(host):
    """Templated formatter.lua is deployed."""
    fmt_file = host.file("/root/.config/nvim/lua/hbuyse/plugins/formatter.lua")
    assert fmt_file.exists
    assert fmt_file.contains("stevearc/conform.nvim")


def test_perlnavigator_lua_exists(host):
    """Templated perlnavigator.lua is deployed."""
    lsp_file = host.file("/root/.config/nvim/lsp/perlnavigator.lua")
    assert lsp_file.exists
    assert lsp_file.contains("perlnavigator")
    assert lsp_file.contains("includePaths")


def test_static_files_are_deployed(host):
    """Static configuration files from files/ are synced."""
    for filename in [".editorconfig", ".gitignore", ".luacheckrc", ".stylua.toml"]:
        filepath = f"/root/.config/nvim/{filename}"
        assert host.file(filepath).exists, f"{filename} should be deployed"


def test_nvim_installed_via_package_when_applicable(host):
    """On Arch, nvim is installed via the package manager."""
    os_id = host.check_output(". /etc/os-release && echo $ID").strip()

    if os_id == "arch":
        assert host.package("neovim").is_installed
