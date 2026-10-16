def test_netrc_file(host):
    """~/.netrc is deployed."""
    netrc = host.file("/root/.netrc")
    assert netrc.is_file
    assert "machine example.com" in netrc.content_string


def test_netrc_is_private(host):
    """The file holds credentials: it is only readable by its owner (curl and git refuse otherwise)."""
    assert oct(host.file("/root/.netrc").mode) == "0o600"
