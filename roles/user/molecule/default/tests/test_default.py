def test_accountsservice_face_copied(host):
    """The face image is copied into AccountsService icons for the connecting user."""
    icon = host.file("/var/lib/AccountsService/icons/root")
    assert icon.exists
    assert icon.is_file
    assert icon.mode == 0o644


def test_home_face_copied(host):
    """The face image is copied into the home directory as ~/.face."""
    face = host.file("/root/.face")
    assert face.exists
    assert face.is_file
    assert face.mode == 0o644


def test_face_files_match(host):
    """Both copies of the face image have identical content."""
    icon = host.file("/var/lib/AccountsService/icons/root")
    face = host.file("/root/.face")
    assert icon.content == face.content
