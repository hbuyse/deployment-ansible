from pathlib import Path



def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()

ROLE_DIR = Path(__file__).resolve().parents[3]


def test_direnv_runs(host):
    """direnv reports its version."""
    cmd = host.run("PATH=/root/.local/bin:$PATH direnv version")
    assert cmd.rc == 0, cmd.stderr
    assert cmd.stdout.strip()[0].isdigit()


def test_installation_method(host):
    """Arch installs the package, the others download the binary and the man pages in ~/.local."""
    if _os_id(host) == "arch":
        assert host.package("direnv").is_installed
        return
    binary = host.file("/root/.local/bin/direnv")
    assert binary.is_file
    assert oct(binary.mode) == "0o755"
    assert host.file("/root/.local/share/man/man1/direnv.1").is_file


def test_direnvrc(host):
    """The direnvrc of the role is deployed."""
    direnvrc = host.file("/root/.config/direnv/direnvrc")
    assert direnvrc.is_file
    assert direnvrc.content_string == (ROLE_DIR / "files" / "direnvrc").read_text()


def test_direnv_toml_is_rendered(host):
    """The whitelist is generated for the user home directory."""
    config = host.file("/root/.config/direnv/direnv.toml")
    assert config.is_file
    assert "{{" not in config.content_string
    assert '"/root/Programming/freebsd-src"' in config.content_string
