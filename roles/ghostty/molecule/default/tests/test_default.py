from pathlib import Path

ROLE_DIR = Path(__file__).resolve().parents[3]
CONFIG = "/root/.config/ghostty"


def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()


def test_ghostty_package(host):
    """Ghostty is installed."""
    assert host.package("ghostty").is_installed
    assert host.exists("ghostty")


def test_ppa_on_ubuntu(host):
    """Ubuntu uses the community PPA."""
    if _os_id(host) == "arch":
        return
    assert "mkasberg/ghostty-ubuntu" in host.file("/etc/apt/sources.list.d/ghostty.sources").content_string


def test_configuration_files(host):
    """The .ghostty files of the role are deployed."""
    sources = list((ROLE_DIR / "files").glob("*.ghostty"))
    assert sources
    for source in sources:
        deployed = host.file(f"{CONFIG}/{source.name}")
        assert deployed.is_file, source.name
        assert deployed.content_string == source.read_text(), source.name


def test_catppuccin_themes(host):
    """The four Catppuccin flavours are downloaded."""
    for flavour in ("frappe", "latte", "macchiato", "mocha"):
        assert host.file(f"{CONFIG}/themes/catppuccin-{flavour}.conf").is_file, flavour


def test_style_sheet_and_service_override(host):
    """The tab style sheet is compiled and the systemd override is deployed."""
    assert host.file(f"{CONFIG}/tab-style.css").size > 0
    override = host.file("/root/.config/systemd/user/app-com.mitchellh.ghostty.service.d/override.conf")
    assert override.is_file
    assert override.content_string == (ROLE_DIR / "files" / "override.conf").read_text()
