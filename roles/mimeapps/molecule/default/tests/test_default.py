def test_mimeapps_list_copied(host):
    """mimeapps.list was copied into the XDG config directory."""
    config_file = host.file("/root/.config/mimeapps.list")
    assert config_file.exists
    assert config_file.is_file
    assert config_file.mode == 0o644


def test_mimeapps_list_content(host):
    """mimeapps.list content matches the expected format."""
    config_file = host.file("/root/.config/mimeapps.list")
    assert "[Default Applications]" in config_file.content_string


def test_mimeapps_deprecated_symlink(host):
    """The deprecated ~/.local/share/applications/mimeapps.list symlink is created."""
    link = host.file("/root/.local/share/applications/mimeapps.list")
    assert link.exists
    assert link.is_symlink
    assert link.linked_to == "/root/.config/mimeapps.list"
