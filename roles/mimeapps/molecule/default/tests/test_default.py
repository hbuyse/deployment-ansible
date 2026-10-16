from pathlib import Path

ROLE_DIR = Path(__file__).resolve().parents[3]


def test_mimeapps_list_is_deployed(host):
    """The mimeapps.list of the role is deployed in ~/.config."""
    deployed = host.file("/root/.config/mimeapps.list")
    assert deployed.is_file
    assert oct(deployed.mode) == "0o644"
    assert deployed.content_string == (ROLE_DIR / "files" / "mimeapps.list").read_text()


def test_mimeapps_list_has_default_applications(host):
    """The file has the section the desktop looks for."""
    assert "[Default Applications]" in host.file("/root/.config/mimeapps.list").content_string


def test_deprecated_location_is_a_link(host):
    """The deprecated ~/.local/share/applications/mimeapps.list points to the file in ~/.config."""
    link = host.file("/root/.local/share/applications/mimeapps.list")
    assert link.is_symlink
    assert link.linked_to == "/root/.config/mimeapps.list"
